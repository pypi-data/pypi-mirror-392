import logging
from pathlib import Path
from typing import Optional, List, Union

import pandas as pd
from tqdm import tqdm

from .pdf_doc import PDFDoc

logger = logging.getLogger(__name__)

class PDFDocBatch:
    def __init__(self):
        self.pdfdocs: list[PDFDoc] = []
    
    def __add__(self, other: Union[List[PDFDoc], "PDFDocBatch"]) -> "PDFDocBatch":
        new_batch = PDFDocBatch.from_pdfdoc_list(self.pdfdocs)
        new_batch.extend(other)
        return new_batch

    def __iadd__(self, other: Union[List[PDFDoc], "PDFDocBatch"]) -> "PDFDocBatch":
        self.extend(other)
        return self
    
    def __iter__(self):
        return iter(self.pdfdocs)
    
    def __getitem__(self, index: int) -> "PDFDoc":
        return self.pdfdocs[index]
    
    def __len__(self):
        return len(self.pdfdocs)
    
    @classmethod
    def from_folder(cls, path: str | Path, recursive: bool = True) -> "PDFDocBatch":
        """Creates a PDFDocBatch from all PDFs in a folder.

        Args:
            path (str | Path): Path to a directory containing PDF files.
            recursive (bool, optional): Whether to search subdirectories
                recursively. Defaults to True.

        Returns:
            PDFDocBatch: A batch containing PDFDoc instances loaded from the folder.
        """
        batch = cls()
        batch.pdfdocs = PDFDoc.from_folder(path, recursive=recursive)
        return batch

    @classmethod
    def from_byte_list(cls, byte_list: List[bytes], names: Optional[List[str]] = None) -> "PDFDocBatch":
        """Creates a PDFDocBatch from a list of PDF byte streams.

        Args:
            byte_list (List[bytes]): A list of PDF file contents as bytes.
            names (List[str], optional): Optional list of names for each PDF
                in `byte_list`. Must match the byte_list length if provided.

        Returns:
            PDFDocBatch: A batch containing PDFDoc objects created from the
                provided byte streams.

        Example:
            batch = PDFDocBatch.from_byte_list([pdf_bytes], names=["file1.pdf, file2.pdf, file3.pdf"])
        """
        batch = cls()
        batch.pdfdocs = PDFDoc.from_byte_list(byte_list, names=names)
        return batch

    @classmethod
    def from_pdfdoc_list(cls, pdfdoc_list: List[PDFDoc]) -> "PDFDocBatch":
        """
        Create a PDFDocBatch from an existing list of PDFDoc instances.
        """
        batch = cls()
        batch.pdfdocs = list(pdfdoc_list)  # make a copy to avoid mutation
        return batch
    
    def extend(self, other: Union[List[PDFDoc], "PDFDocBatch"]) -> None:
        """Extend this batch with more PDFDoc objects or another PDFDocBatch."""
        if isinstance(other, PDFDocBatch):
            self.pdfdocs.extend(other.pdfdocs)
        elif isinstance(other, list):
            if all(isinstance(doc, PDFDoc) for doc in other):
                self.pdfdocs.extend(other)
            else:
                raise TypeError("All items in the list must be PDFDoc instances.")
        else:
            raise TypeError("Argument must be a PDFDocBatch or a list of PDFDoc instances.")
    
    def append(self, pdfdoc: PDFDoc) -> None:
        """Append a PDFDoc to this batch."""
        if not isinstance(pdfdoc, PDFDoc):
            raise TypeError("Only PDFDoc instances can be appended.")
        
        self.pdfdocs.append(pdfdoc)

    def search_signature(
        self, 
        keywords: List[str],
        exact: bool = False,
        max_distance: int = 70,
        save_folder: Optional[str | Path] = None,
        min_contrast: int = 30,
        filter_stroke_density: bool = True,
        enforce_text_type: bool = True
    ) -> "PDFDocBatch":
        """Detects handwritten or scanned signatures associated with keyword regions for multiple PDFs.

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
            PDFDocBatch: A new batch where each PDFDoc contains signature
                search results.
        """
        new_docs = []
        for doc in tqdm(self.pdfdocs, desc='Searching signatures in PDFs'):
            try:
                result = doc.search_signature(keywords, exact=exact, max_distance=max_distance, save_folder=save_folder, min_contrast=min_contrast,
                                              filter_stroke_density=filter_stroke_density, enforce_text_type=enforce_text_type)
                new_docs.append(result)

            except Exception as e:
                logger.exception(f"Failed to process {doc.name}: {e}")

        return PDFDocBatch.from_pdfdoc_list(new_docs)

    def search_header(self, keywords: list[str], exact=True) -> "PDFDocBatch":
        """Searches PDF headers for the given keywords. Always case insensitive.

        Args:
            keywords (list[str]): Keywords to search within PDF headers.
            exact (bool, optional): Whether to match keywords exactly or instead allow partial matching.
                Defaults to True.

        Returns:
            PDFDocBatch: A batch containing the results of the header search.
        """
        new_docs = []
        for doc in tqdm(self.pdfdocs, desc='Searching headers in PDFs'):
            try:
                result = doc.search_header(keywords, exact=exact, as_tuple=False)
                new_docs.append(result)

            except Exception as e:
                logger.exception(f"Failed to process {doc.name}: {e}")

        return PDFDocBatch.from_pdfdoc_list(new_docs)

    def search_body(self, keywords: list[str], exact=True) -> "PDFDocBatch":
        """Searches PDF body for specific keywords. Always case insensitive.

        Args:
            keywords (list[str]): Keywords to search in the body content.
            exact (bool, optional): Whether to require exact matching or instead allow partial matching.
                Defaults to True.

        Returns:
            PDFDocBatch: A batch with updated body search results.
        """
        new_docs = []
        for doc in tqdm(self.pdfdocs, desc='Searching bodies in PDFs'):
            try:
                result = doc.search_body(keywords, exact=exact, as_tuple=False)
                new_docs.append(result)

            except Exception as e:
                logger.exception(f"Failed to process {doc.name}: {e}")

        return PDFDocBatch.from_pdfdoc_list(new_docs)

    def search_by_meaning(self, query: str, threshold: float = 0, chunk_by="section",
                          word_count: int = 5, buffer_size: int = 1, chunk_text_semantically_threshold: float = 0.3, max_results = 5) -> "PDFDocBatch":
        """Performs semantic (meaning-based) search across all PDFs.

        Args:
            query (str): The semantic search query.
            threshold (float, optional): Minimum similarity score for a match.
                Defaults to 0.
            chunk_by (str, optional): Text chunking mode (e.g., "section").
                Defaults to "section".
            word_count (int, optional): Minimum number of words per chunk.
                Defaults to 5.
            buffer_size (int, optional): Overlap size between chunks.
                Defaults to 1.
            chunk_text_semantically_threshold (float, optional): Semantic
                chunking threshold. Defaults to 0.3.
            max_results (int, optional): Maximum results per PDF. Defaults to 5.

        Returns:
            PDFDocBatch: A batch containing semantic search results for each PDF.
        """ 
        new_docs = []
        for doc in tqdm(self.pdfdocs, desc='Searching PDFs by meaning'):
            try:
                result = doc.search_by_meaning(
                    query,
                    threshold=threshold,
                    chunk_by=chunk_by,
                    word_count=word_count,
                    buffer_size=buffer_size,
                    chunk_text_semantically_threshold=chunk_text_semantically_threshold,
                    as_tuple=False,
                    max_results=max_results,
                )
                new_docs.append(result)

            except Exception as e:
                logger.exception(f"Failed to process {doc.name}: {e}")

        return PDFDocBatch.from_pdfdoc_list(new_docs)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Converts batch data into a combined pandas DataFrame.

        The resulting DataFrame contains one row per PDF, merging all extracted
        fields from individual PDFDoc objects. PDF with same names are combined and overwrite each other

        Returns:
            pandas.DataFrame: A DataFrame representing aggregated PDF analysis.
        """
        combined_data = {}

        for pdf in self.pdfdocs:
            df = pdf.to_dataframe()
            pdf_name = df["pdf_name"].iloc[0]  # Get the single value from the single-row DF

            if pdf_name not in combined_data:
                combined_data[pdf_name] = df.iloc[0].to_dict()
            else:
                # Merge columns into existing row
                for col, val in df.iloc[0].items():
                    if col != "pdf_name":
                        combined_data[pdf_name][col] = val

        if not combined_data:
            return pd.DataFrame()

        combined_df = pd.DataFrame(list(combined_data.values()))
        cols = ["pdf_name"] + [c for c in combined_df.columns if c != "pdf_name"]
        combined_df = combined_df[cols]

        return combined_df
    
    def to_excel(self, path: str | Path, sheet_name: str = "Sheet1"):
        """Exports the batch data to an Excel (.xlsx) file.

        Args:
            path (str | Path): Output file location.
            sheet_name (str, optional): Name of the worksheet. Defaults to "Sheet1".

        Returns:
            None
        """
        df = self.to_dataframe()
        df.to_excel(path, sheet_name=sheet_name, index=False)

    def to_csv(self, path: str | Path):
        """Exports the batch data to a CSV file.

        Args:
            path (str | Path): Path to the output CSV file.

        Returns:
            None
        """
        df = self.to_dataframe()
        df.to_csv(path, index=False)