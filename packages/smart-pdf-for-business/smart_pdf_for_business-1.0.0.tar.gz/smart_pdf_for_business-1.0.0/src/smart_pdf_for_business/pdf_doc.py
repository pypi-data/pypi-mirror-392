import re
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import overload, Optional, Dict, Any, List, Tuple, Literal

import numpy as np
import pandas as pd
import spacy
import srsly
from sentence_transformers import util, SentenceTransformer
from spacy_layout import spaCyLayout
from spacy_layout.layout import Doc
from tqdm import tqdm

from .signature_detector import SignatureDetector, Signature
from .utils import chunk_text_semantically, save_signatures, center_of, distance_of

_shared_model = SentenceTransformer('all-MiniLM-L6-v2')
_shared_signature_detector = SignatureDetector()
_shared_spacy_layout = spaCyLayout(spacy.blank("en"))


try:
    _shared_nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli.download import download
    download('en_core_web_sm')
    _shared_nlp = spacy.load("en_core_web_sm")


signature_whitelist = { 
    "PERSON",     # Signer name
    "ORG",        # Company/agency
    "GPE",        # Countries/cities/states
    "LOC",        # Locations
    "FAC",        # Facilities
    "NORP",       # Nationalities/groups
    "DATE",       # Signature dates
    "TIME",       # Signature times
    "CARDINAL",   # Numbers used in forms
    "ORDINAL",    # 'Section 1', 'Part II'
    "LAW",        # Legal references
    "MONEY",      # Contract sections with money near signatures
    "EVENT",      # Named events
    "WORK_OF_ART" # Document titles in headers/footers
}

@dataclass
class PDFDoc:
    data: bytes 
    path: Optional[Path] = None
    name: Optional[str] = None
    spacy_doc: Optional[Doc] = None
    sections: List[Tuple[str, str]] = field(default_factory=list)
    weighted_sections: List[Tuple[Tuple[str, str], float]] = field(default_factory=list)
    signatures: List[Signature] = field(default_factory=list)
    model: SentenceTransformer = _shared_model
    signature_detector: SignatureDetector = _shared_signature_detector
    spacy_layout: spaCyLayout = _shared_spacy_layout
    nlp: spacy.language.Language = _shared_nlp

    def __post_init__(self):
            if not self.spacy_doc:
                self.spacy_doc = self.spacy_layout(self.data)

            if not self.sections: 
                markdown_text = self.spacy_doc._.markdown  # type: ignore
                
                pattern = r'^(#+)\s+(.*?)\s*$'
                matches = list(re.finditer(pattern, markdown_text, flags=re.MULTILINE))

                sections = []

                for i, match in enumerate(matches):
                    title = match.group(2).strip()
                    start = match.end()
                    end = matches[i+1].start() if i + 1 < len(matches) else len(markdown_text)
                    body = markdown_text[start:end].strip()
                    sections.append((title, body))

                self.sections = sections

    def __str__(self):
        return self.to_text()

    @classmethod
    def from_file(cls, path: str | Path) -> "PDFDoc":
        """Creates a PDFDoc from a PDF file."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"File is not a PDF: {file_path.name}")

        return cls(
            data=file_path.read_bytes(),
            path=file_path,
            name=file_path.name
        )
    
    @classmethod
    def from_folder(cls, folder_path: str | Path, recursive: bool = True) -> List["PDFDoc"]:
        """Creates a list of PDFDoc from all PDFs in a folder.

        Args:
            path (str | Path): Path to a directory containing PDF files.
            recursive (bool, optional): Whether to search subdirectories
                recursively. Defaults to True.

        Returns:
            list of PDFDoc: A list of PDFDoc instances.
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")

        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = sorted(folder.glob(pattern))

        if not pdf_files:
            print(f"[Warning] No PDF files found in {folder}")
            return []

        docs = []
        for file in tqdm(pdf_files, desc="Loading PDFs from folder"):
            docs.append(cls(
                data=file.read_bytes(),
                path=file,
                name=file.name
            ))

        return docs

    @classmethod
    def from_bytes(cls, data: bytes, name: Optional[str] = None) -> "PDFDoc":
        """Creates a PDFDoc from raw PDF bytes.

        Args:
            data (bytes): Byte content of a PDF file.
            name (str, optional): Name to assign to the document. Defaults to
                "file.pdf".

        Returns:
            PDFDoc: A PDFDoc instance created from bytes.
        """
        if not name:
            name = "file.pdf"
        return cls(data=data, name=name)

    @classmethod
    def from_byte_list(cls, byte_list: List[bytes], names: Optional[List[str]] = None) -> List["PDFDoc"]:
        """Creates a list of PDFDoc objects from a list of PDF byte streams.

        Args:
            byte_list (list[bytes]): List of PDF byte sequences.
            names (list[str], optional): Corresponding list of document names.
                If fewer names than byte streams are provided, generated names
                are appended. If more are provided, the list is truncated.

        Returns:
            list[PDFDoc]: A list of PDFDoc instances.
        """
        if names is None:
            names = [f"file_{i}.pdf" for i in range(len(byte_list))]
        elif len(names) < len(byte_list):
            for i in range(len(names), len(byte_list)):
                names.append(f"file_{i}.pdf")
        elif len(names) > len(byte_list):
            names = names[:len(byte_list)]

        docs = []
        for i, data in tqdm(enumerate(byte_list), total=len(byte_list), desc="Loading PDFs from byte list"):
            docs.append(cls(data=data, name=names[i]))

        return docs
    
    def search_signature(
        self, 
        keywords: List[str],
        exact: bool = False,
        max_distance: int = 70,
        save_folder: Optional[str | Path] = None,
        min_contrast: int = 30,
        filter_stroke_density: bool = True,
        enforce_text_type: bool = True
    ) -> List["Signature"]:
        """Detects handwritten or scanned signatures associated with keyword regions.

        Signature detection combines OCR text, spatial layout analysis, and
        signature bounding boxes to identify signatures close to specified
        keywords.

        Args:
            keywords (list[str]): Keywords used to locate signature-related
                regions.
            exact (bool, optional): Whether keyword matching must be exact.
                Defaults to False.
            max_distance (int, optional): Maximum pixel distance between a
                keyword block and signature for a valid match. Defaults to 70.
            save_folder (str | Path | None, optional): If provided, saves
                cropped signature images to this directory. Defaults to None.
            min_contrast (int, optional): Minimum pixel contrast threshold used
                by the signature detector. Defaults to 30. Setting to 0 will disable contrast filtering
            filter_stroke_density (bool, optional): Whether to filter image
                regions based on stroke density. Defaults to True.
            enforce_text_type (bool, optional): Whether to filter signature text
                 based on stroke density. Defaults to True.

        Returns:
            list[Signature]: A list of matched signature objects.

        Side Effects:
            Updates ``self.signatures`` with detected signatures.
        """
        results = []
        pages = self.spacy_doc._.pages #type: ignore
        
        all_signatures, all_ocr_text = self.signature_detector.detect(self.data, min_contrast = min_contrast, filter_stroke_density = filter_stroke_density)
        punct_table = str.maketrans("", "", string.punctuation)
        cleaned_data = []
        for page_no, items in all_ocr_text:
            new_items = []
            for text, bbox in items:
                for kw in keywords:
                    text = text.replace(kw, "")

                text = text.translate(punct_table).replace(" ", "")

                if enforce_text_type:
                    doc = self.nlp(text)

                    text = any(
                        ent.label_ in signature_whitelist
                        for ent in doc.ents
                    )

                if text:
                    new_items.append((text, bbox))

            if new_items:
                cleaned_data.append((page_no, new_items))

        keyword_blocks = []
        for page, spans in pages:
            page.page_no
            page_ocr_text = next((ocr for p_no, ocr in cleaned_data if p_no == page.page_no), [])
            for span in spans:

                text = span.text.lower()
                for kw in keywords:
                    kw_lower = kw.lower()
                    if exact:
                        found = re.search(rf'\b{re.escape(kw_lower)}\b', text)
                    else:
                        found = kw_lower in text

                    if found and span._.layout:
                        # Calculate coordinates
                        layout = span._.layout
                        coords = (layout.x, layout.y, layout.x + layout.width, layout.y + layout.height)

                        keyword_blocks.append({
                            "keyword": kw,
                            "coords": coords,
                            "page_number": layout.page_no
                        })

            signatures = [sig for sig in all_signatures if sig.page == page.page_no]

            if not keyword_blocks or not signatures:
                continue

            candidate_pairs = []

            # Build all possible (signature, keyword) pairs within range
            for sig in signatures:
                if sig.bbox is None:
                    continue

                sig_center = center_of(sig.bbox)

                for k_idx, kb in enumerate(keyword_blocks):
                    x0, y0, x1b, y1b = kb["coords"]
                    kw_center = ((x0 + x1b) // 2, (y0 + y1b) // 2)
                    distance = np.sqrt(
                        (sig_center[0] - kw_center[0]) ** 2 +
                        (sig_center[1] - kw_center[1]) ** 2
                    )
                    if distance <= max_distance:
                        viable_ocr = []
                        for ocr_text, ocr_bbox in page_ocr_text:
                            ocr_distance_kw = distance_of(kw_center, center_of(ocr_bbox))
                            ocr_distance_sig = distance_of(sig_center, center_of(ocr_bbox))

                            if ocr_distance_kw <= max_distance or ocr_distance_sig <= max_distance:
                                viable_ocr.append((ocr_text, ocr_bbox, min(ocr_distance_kw, ocr_distance_sig)))

                        if viable_ocr:
                            viable_ocr.sort(key=lambda x: x[2])  # sort by distance
                            closest_text, _, _ = viable_ocr[0]
                            candidate_pairs.append((sig, k_idx, distance, closest_text))
                        else:
                            candidate_pairs.append((sig, k_idx, distance, ""))

            # Sort pairs by distance (smallest first)
            candidate_pairs.sort(key=lambda x: x[2])
            matched_signatures = []
            used_sigs = []
            used_keywords = []

            for sig, k_idx, dist, flav_text in candidate_pairs:
                if sig in used_sigs or k_idx in used_keywords:
                    continue

                used_sigs.append(sig)
                used_keywords.append(k_idx)

                sig.distance = round(dist, 2)
                sig.keyword = keyword_blocks[k_idx]["keyword"]
                sig.text = flav_text

                matched_signatures.append(sig)

            if matched_signatures:
                results.extend(matched_signatures)

        if save_folder is not None:
            save_signatures(save_folder, results)

        self.signatures = results
        return results


    @overload
    def search_header(self, keywords: list[str], *, exact:bool=True, as_tuple: Literal[False] = False) -> "PDFDoc": ...
    
    @overload
    def search_header(self, keywords: list[str], *, exact:bool=True, as_tuple: Literal[True]) -> List[Tuple[str, str]]: ...
    
    def search_header(self, keywords: list[str], *, exact:bool=True, as_tuple: bool = False):
        """Searches section headers for keyword matches. Always case insensitive

        Args:
            keywords (list[str]): Keywords to search for in section titles.
            exact (bool, optional): Whether to use exact word matching instead
                of substring matching. Defaults to True.
            as_tuple (bool, optional): If True, returns a list of
                (header, body) tuples instead of a new PDFDoc. Defaults to False.

        Returns:
            PDFDoc | list[tuple[str, str]]: Either a new PDFDoc containing only
            matched sections or a list of section tuples.
        """
        results = []

        keywords = [k.lower() for k in keywords]

        new_metadata = {"result_of": "search_header"}

        for title, body in self.sections:
            title_lower = title.lower()

            if exact:
                found = any(re.search(rf'\b{re.escape(k)}\b', title_lower) for k in keywords)
            else:
                found = any(k in title_lower for k in keywords)

            if found:
                results.append((title,body))

        if as_tuple:
            return results
        
        else:
            new_doc = PDFDoc(
            data=self.data,
            path=self.path,
            name=self.name,
            spacy_doc=self.spacy_doc,
            sections=results,
            signatures=self.signatures.copy()
            )

            return new_doc
    
    
    @overload
    def search_body(self, keywords: list[str], *, exact: bool = True, as_tuple: Literal[False] = False) -> "PDFDoc": ...
        
    @overload
    def search_body(self, keywords: list[str], *, exact: bool = True, as_tuple: Literal[True]) -> List[Tuple[str, str]]: ...

    def search_body(self, keywords: list[str], *, exact: bool = True, as_tuple: bool = False):
        """Searches section body for keyword matches. Always case insensitive

        Args:
            keywords (list[str]): Keywords to search for in section titles.
            exact (bool, optional): Whether to use exact word matching instead
                of substring matching. Defaults to True.
            as_tuple (bool, optional): If True, returns a list of
                (header, body) tuples instead of a new PDFDoc. Defaults to False.

        Returns:
            PDFDoc | list[tuple[str, str]]: Either a new PDFDoc containing only
            matched sections or a list of section tuples.
        """
        results = []

        keywords = [k.lower() for k in keywords]

        new_metadata = {"result_of": "search_body"}

        for title, body in self.sections:
            body_lower = body.lower()

            if exact:
                found = any(re.search(rf'\b{re.escape(k)}\b', body_lower) for k in keywords)
            else:
                found = any(k in body_lower for k in keywords)

            if found:
                results.append((title,body))

        if as_tuple:
            return results
        
        else:
            new_doc = PDFDoc(
            data=self.data,
            path=self.path,
            name=self.name,
            spacy_doc=self.spacy_doc,
            sections=results,
            signatures=self.signatures.copy()
            )

            return new_doc
    
    @overload
    def search_by_meaning(
        self,
        query: str,
        *,
        threshold: float = 0,
        chunk_by: str = "section",
        as_tuple: Literal[False] = False,
        word_count: int = 5,
        buffer_size: int = 1,
        chunk_text_semantically_threshold: float = 0.3,
        max_results: int = 5
    ) -> "PDFDoc": ...

    @overload
    def search_by_meaning(
        self,
        query: str,
        *,
        threshold: float = 0,
        chunk_by: str = "section",
        as_tuple: Literal[True],
        word_count: int = 5,
        buffer_size: int = 1,
        chunk_text_semantically_threshold: float = 0.3,
        max_results: int = 5
    ) -> List[Tuple[Tuple[str, str], float]]: ...

    def search_by_meaning(
        self,
        query: str,
        *,
        threshold: float = 0,
        chunk_by: str = "section",
        as_tuple: bool = False,
        word_count: int = 5,
        buffer_size: int = 1,
        chunk_text_semantically_threshold: float = 0.3,
        max_results: int = 5
    ):
        """Performs semantic search across sections, chunks, sentences, or paragraphs.

        Embeds the query using SentenceTransformer and computes cosine
        similarity against document chunks, returning the best semantic matches.

        Args:
            query (str): Natural-language query string.
            threshold (float, optional): Minimum similarity score to keep a
                match. Defaults to 0.
            chunk_by (str, optional): Chunking method: ``"section"``,
                ``"semantic"``, ``"sentence"``, ``"paragraph"``, or ``"word"``.
                Defaults to "section".
            as_tuple (bool, optional): If True, returns raw semantic match
                tuples. Defaults to False.
            word_count (int, optional): Word count per chunk when using word
                chunking. Defaults to 5.
            buffer_size (int, optional): Overlap size for when using semantic 
                chunking. Defaults to 1.
            chunk_text_semantically_threshold (float, optional): Similarity
                threshold for when building for semantic chunking . Defaults to 0.3.
            max_results (int, optional): Maximum number of highest-scoring
                results. Defaults to 5.

        Returns:
            PDFDoc | list[tuple[tuple[str, str], float]]: Either a new PDFDoc
            containing only matched sections or a list of weighted chunks.
        """
        results = []

        query_embedding = self.model.encode(query, convert_to_tensor=True, show_progress_bar=False)

        new_metadata = {"result_of": "search_by_meaning", "chunk_by":chunk_by, "threshold": threshold}

        match chunk_by:
            case "section":
                for title, body in self.sections:
                    section_text = f"{title}\n{body}"
                    section_embedding = self.model.encode(section_text, convert_to_tensor=True, show_progress_bar=False)
                    similarity = util.cos_sim(query_embedding, section_embedding).item()
                    if similarity >= threshold:
                        results.append(((f"{query}_result_{len(results)}", section_text), round(similarity, 3)))

            case "semantic":
                semantic_chunks = chunk_text_semantically(self.to_text() ,self.model ,buffer_size=buffer_size, similarity_threshold=chunk_text_semantically_threshold)

                for chunk in semantic_chunks:
                    chunk_embedding = self.model.encode(chunk, convert_to_tensor=True, show_progress_bar=False)
                    similarity = util.cos_sim(query_embedding, chunk_embedding).item()

                    if similarity >= threshold:
                        results.append(((f"{query}_result_{len(results)}", chunk), round(similarity, 3)))

            case "sentence":
                text = self.to_text()
                sentences = [s.strip() for s in text.split(".") if s.strip()]

                for sentence in sentences:
                    sentence_embedding = self.model.encode(sentence, convert_to_tensor=True, show_progress_bar=False)
                    similarity = util.cos_sim(query_embedding, sentence_embedding).item()

                    if similarity >= threshold:
                        results.append(((f"{query}_result_{len(results)}", sentence), round(similarity, 3)))

            case "paragraph":
                text = self.to_text()
                paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

                for paragraph in paragraphs:
                    paragraph_embedding = self.model.encode(paragraph, convert_to_tensor=True, show_progress_bar=False)
                    similarity = util.cos_sim(query_embedding, paragraph_embedding).item()

                    if similarity >= threshold:
                        results.append(((f"{query}_result_{len(results)}", paragraph), round(similarity, 3)))

            case "word":
                text = self.to_text()
                words = [w for w in text.split() if w.isalpha()]
                n = max(1, word_count)

                for i in range(0, len(words), n):
                    chunk = " ".join(words[i:i + n])
                    if not chunk.strip():
                        continue

                    chunk_embedding = self.model.encode(chunk, convert_to_tensor=True, show_progress_bar=False)
                    similarity = util.cos_sim(query_embedding, chunk_embedding).item()

                    if similarity >= threshold:
                        results.append(((f"{query}_result_{len(results)}", chunk), round(similarity, 3)))

        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:max_results]

        if as_tuple:
            return results
        
        else:
            new_doc = PDFDoc(
            data=self.data,
            path=self.path,
            name=self.name,
            spacy_doc=self.spacy_doc,
            sections=[pair for pair, _ in results],
            weighted_sections=results,
            signatures=self.signatures.copy()
            )
            return new_doc
    

    def to_text(self, annotate_signatures: bool = True) -> str:
        """Returns the document as plain text, optionally annotated with signature info."""
        text_output = []

        for topic, body in self.sections:
            section_text = f"{topic}\n{body}"

            if annotate_signatures and self.signatures:
                lines = section_text.split("\n")
                for sig in self.signatures:
                    print(sig)
                    kw = sig.keyword.lower() if sig.keyword else None
                    bbox = sig.bbox
                    note = f" [SIGNED: '{sig.text}' at bbox {bbox}]"
                    for i, line in enumerate(lines):
                        if kw and kw in line.lower():
                            lines[i] = line + note
                            break
                section_text = "\n".join(lines)

            text_output.append(section_text)

        return "\n\n".join(text_output)

    def to_markdown(self, annotate_signatures: bool = True) -> str:
        """Return the document as plain markdown, optionally annotated with signature info."""
        markdown_text = self.spacy_doc._.markdown  # type: ignore

        if annotate_signatures and self.signatures:
            lines = markdown_text.split("\n")
            for sig in self.signatures:
                kw = sig.keyword.lower() if sig.keyword else None 
                bbox = sig.bbox
                note = f" **[SIGNED: '{sig.text}' at bbox {bbox}]**"
                for i, line in enumerate(lines):
                    if kw in line.lower():
                        lines[i] = line + note
                        break
            markdown_text = "\n".join(lines)

        return markdown_text
    
    def to_dataframe(self) -> pd.DataFrame:
        """Converts extracted document content into a pandas DataFrame.

        The table contains section names, their bodies, detected signatures,
        and semantic match weights.

        Returns:
            pandas.DataFrame: Tabular representation of extracted content.
        """
        data = {}
        data["pdf_name"] = [self.name]

        for title, body in self.sections:
            data[title] = [body]

        for sig in self.signatures:
            kw = sig.keyword or "Unknown"
            bbox = sig.bbox
            flavor_text = f"**[SIGNED: '{sig.text}' at bbox {bbox}]**"
            data[f"Signature: {kw}"] = [flavor_text]
            
        for (title, _), weight in self.weighted_sections:
            col_name = f"{title}_weightage"
            data[col_name] = [weight]
        
        df = pd.DataFrame(data)
        return df
    
    def to_excel(self, path: str | Path, sheet_name: str = "Sheet1"):
        """Exports the document's DataFrame representation to an Excel file.

        Args:
            path (str | Path): Destination .xlsx file path.
            sheet_name (str, optional): Sheet name for Excel output.
                Defaults to "Sheet1".
        """
        df = self.to_dataframe()
        df.to_excel(path, sheet_name=sheet_name, index=False)

    def to_csv(self, path: str | Path):
        """Exports the document's DataFrame representation to a CSV file.

        Args:
            path (str | Path): Output CSV file path.
        """
        df = self.to_dataframe()
        df.to_csv(path, index=False)

    def to_json(self, path: Optional[str | Path] = None, indent: int = 2) -> str:
        """Serializes the document into JSON format.

        Args:
            path (str | Path | None, optional): If provided, writes the JSON
                output to this file. Defaults to None.
            indent (int, optional): JSON indentation spacing. Defaults to 2.

        Returns:
            str: The serialized JSON string.
        """
        data = {
            "name": self.name,
            "path": str(self.path) if self.path else None,
            "sections": [{"title": t, "body": b} for t, b in self.sections],
            "signatures": [
                {
                    "keyword": sig.keyword,
                    "text": sig.text,
                    "bbox": sig.bbox,
                    "page": sig.page,
                    "distance": sig.distance,
                }
                for sig in self.signatures
            ],
        }

        # Serialize to JSON string
        json_str = srsly.json_dumps(data, indent=indent)

        # Optionally write to file
        if path:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            srsly.write_json(file_path, data, indent=indent)

        return json_str