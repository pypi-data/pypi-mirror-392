from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List

import cv2
import numpy as np
import pymupdf
from rapidocr import RapidOCR
from skimage import measure, morphology

from .utils import center_of

@dataclass
class Signature:
    keyword: Optional[str] = None
    text: Optional[str] = None      
    bbox: Optional[Tuple[int, int, int, int]] = None
    page: Optional[int] = None
    img: Optional[np.ndarray] = None
    distance: Optional[float] = None

class SignatureDetector:
    def __init__(self, small_const1=84, small_const2=250, small_const3=100, big_mult=18,
                 min_fill=0.01, max_fill=0.3):
        self.c1 = small_const1
        self.c2 = small_const2
        self.c3 = small_const3
        self.big_mult = big_mult
        self.min_fill = min_fill
        self.max_fill = max_fill
        self.ocr = RapidOCR()

    def _pdf_page_to_gray(self, pdf_bytes):
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        gray_pages = []

        for page in doc:
            pix = page.get_pixmap()  # default RGBA
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n > 1:
                # Convert RGB/RGBA to grayscale
                img_gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
            else:
                img_gray = img
            gray_pages.append(img_gray)

        return gray_pages

    def _process_image(self, img):
        # Adaptive thresholding (better for uneven backgrounds)
        img_bin = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 15, 8
        )

        blobs = img_bin > 0
        blobs_labels = measure.label(blobs, background=0)

        # Compute average and largest region
        total_area = 0
        counter = 0
        biggest = 0
        for region in measure.regionprops(blobs_labels):
            if region.area > 10:
                total_area += region.area
                counter += 1
            if region.area >= 250 and region.area > biggest:
                biggest = region.area

        avg = (total_area / counter) if counter else 0
        small_cut = ((avg / self.c1) * self.c2) + self.c3
        big_cut = small_cut * self.big_mult

        # Remove small and too big objects
        pre = morphology.remove_small_objects(blobs_labels, min_size=max(1, int(small_cut)))
        component_sizes = np.bincount(pre.ravel())
        too_big = component_sizes > big_cut
        mask = too_big[pre]
        pre[mask] = 0

        # Final binary mask
        mask = (pre > 0).astype("uint8") * 255
        return mask

    def detect(self, pdf_bytes, min_contrast=30, filter_stroke_density = True) -> Tuple[
    List[Signature],
    List[Tuple[int, List[Tuple[str, Tuple[float, float, float, float]]]]]
    ]:
        """
        Detects handwritten-style signature regions in a PDF and extracts nearby OCR text.

        This method performs the full signature-detection pipeline:
        1. Converts each PDF page into a grayscale bitmap.
        2. Applies adaptive thresholding and morphological filtering to isolate
        scribble-like ink regions.
        3. Removes objects that are too small or too large based on dynamic
        thresholds derived from page statistics.
        4. Computes bounding boxes for remaining candidate regions.
        5. Filters candidates using stroke density and pixel contrast.
        6. Runs OCR on the cleaned page and returns simplified text + bounding box
        results.

        Args:
            pdf_bytes (bytes):
                Raw PDF file bytes.
            min_contrast (int, optional):
                Minimum required grayscale contrast for a region to be considered a
                signature. Regions with standard deviation below this threshold are
                discarded. Defaults to 30.
            filter_stroke_density (bool, optional):
                Whether to filter regions using calculated stroke-density
                (fill-ratio). If `True`, regions whose ink density falls outside the
                configured `min_fill` / `max_fill` range are removed. Defaults to
                True.

        Returns:
            Tuple[
                List[Signature],
                List[Tuple[int, List[Tuple[str, Tuple[float, float, float, float]]]]]
            ]:
                A tuple containing:

                * **signatures** (`List[Signature]`)  
                A list of detected signature candidates. Each item includes:
                - bounding box `(x1, y1, x2, y2)`
                - page number
                - cropped image region
                - (optional) later-assigned metadata (e.g., keyword, text, distance)

                * **page_ocr** (`List[Tuple[int, List[(text, bbox)]]]`)  
                OCR results for each page as `(page_number, ocr_items)` where:
                - `text` is the recognized OCR string  
                - `bbox` is the text bounding box `(x1, y1, x2, y2)`  

        Raises:
            None explicitly. Errors may propagate from PDF rendering, OpenCV, or OCR
            backends.

        Notes:
            * This method is **low-level** and is not meant to be used directly for
            final signature validation or keyword matching.
            * **Please use `PDFDoc.search_signature()` for the intended public-facing workflow.**
            It wraps this method and handles:
                - keyword matching
                - OCR text proximity analysis
                - signature-to-keyword pairing
                - filtering & annotation
            * Bounding boxes come from connected-component analysis and are not
            rotated; all coordinates are axis-aligned.
        """
        gray_pages = self._pdf_page_to_gray(pdf_bytes)
        results = []
        page_ocr = []

        for i, img in enumerate(gray_pages):
            page_img = img.copy()
            mask = self._process_image(img)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                bbox = (x, y, x + w, y + h)

                if filter_stroke_density:
                    mask_roi = mask[y:y+h, x:x+w]
                    fill_ratio = np.sum(mask_roi > 0) / (w * h)
                    if not (self.min_fill <= fill_ratio <= self.max_fill):
                        continue

                roi_gray = img[y:y+h, x:x+w]
                contrast = np.std(roi_gray)
                if contrast < min_contrast:
                    continue
                
                result = Signature(bbox=bbox, page=i+1, img=roi_gray)
                results.append(result)

                page_img[y:y+h, x:x+w] = 255
            
            ocr_texts = self.simplify_ocr_output(self.ocr(page_img))
            page_ocr.append((i+1, ocr_texts))
        return results, page_ocr
    
    @staticmethod
    def simplify_ocr_output(ocr_result):
        simplified = []
        for box, text in zip(ocr_result.boxes, ocr_result.txts):
            # box: 4 points [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            x_coords = box[:, 0]
            y_coords = box[:, 1]
            x1, y1 = x_coords.min(), y_coords.min()  # top-left
            x2, y2 = x_coords.max(), y_coords.max()  # bottom-right
            simplified.append((text, (x1, y1, x2, y2)))
        return simplified