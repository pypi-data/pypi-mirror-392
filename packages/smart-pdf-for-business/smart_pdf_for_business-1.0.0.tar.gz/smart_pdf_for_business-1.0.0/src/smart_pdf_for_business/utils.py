from typing import List, Tuple
from sentence_transformers import util
from pathlib import Path
import cv2
import numpy as np

def chunk_text_semantically(text, model, buffer_size: int = 1, similarity_threshold: float = 0.3) -> List[str]:
        sent_list = [s.strip() for s in text.split("\n") if s.strip()]

        if not sent_list:
            return []

        n = len(sent_list)
        combined_texts = []
        for i in range(n):
            parts = []
            for j in range(i - buffer_size, i):
                if 0 <= j < n:
                    parts.append(sent_list[j])
            parts.append(sent_list[i])
            for j in range(i + 1, i + 1 + buffer_size):
                if 0 <= j < n:
                    parts.append(sent_list[j])
            combined_texts.append(" ".join(parts))

        embeddings = model.encode(combined_texts, convert_to_tensor=True, show_progress_bar=False)

        distances = []
        for i in range(len(embeddings) - 1):
            sim = util.cos_sim(embeddings[i], embeddings[i + 1]).item()
            dist = 1.0 - float(sim)
            distances.append(dist)

        break_indices = [i for i, d in enumerate(distances) if d > similarity_threshold]

        chunks: List[str] = []
        start = 0
        for idx in break_indices:
            end = idx
            group = sent_list[start : end + 1]
            chunks.append(" ".join(group))
            start = end + 1

        if start < n:
            chunks.append(" ".join(sent_list[start:]))

        return chunks

def save_signatures(folder, signatures):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    for idx, sig in enumerate(signatures):
        if sig.img is None:
            continue

        # Use sig.text as base filename
        base = sig.text if hasattr(sig, "text") and sig.text else f"signature_{idx}"

        # Sanitize minimally
        safe = "".join(c for c in base if c.isalnum() or c in ("_", "-"))

        out_path = folder / f"{safe}_{idx}.png"

        # Save directly with OpenCV
        cv2.imwrite(str(out_path), sig.img)


def center_of(bbox: Tuple[int, int, int, int] | Tuple[float, float, float, float]):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def distance_of(pt1, pt2):
    return np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)