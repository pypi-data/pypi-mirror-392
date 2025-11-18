
# Smart PDF for Business: Extract Text, Headings, and Signatures from PDFs



**Smart PDF for Business** is a Python library for structured PDF content analysis, built on top of **[spaCy-layout](https://github.com/explosion/spacy-layout/tree/main?tab=readme-ov-file)**.
Using spaCy-layout’s page, block, and layout-aware text extraction capabilities, the library adds higher-level features for business workflows and document automation. Smart PDF for Business provides a unified interface to extract, search, and analyze PDF documents with structure-aware intelligence:

* Load PDFs from files, folders, or raw bytes.
* Extract headings, body text, sections, and layout-aware content.
* Search text using **keywords** or **semantic similarity** powered by SentenceTransformers.
* Detect handwritten or scanned **signatures** with bounding boxes, pages, and optional cropped images.
* Export results as **plain text**, **Markdown**, **CSV**, **Excel**, or **JSON**.
* Process **multiple PDFs at once** with batch utilities.

[![PyPI Version](https://img.shields.io/pypi/v/smart_pdf_for_business.svg?style=flat-square&logo=pypi)](https://pypi.org/project/smart_pdf_for_business/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
## 📝 Usage

> ⚠️ This package requires Python 3.10 or above.

```bash
pip install smart_pdf_for_business
```
After initialising a `PDFDoc` object using one of the factory methods, you can call its built-in functions. Most methods create a new  `PDFDoc` object containing the result. This allows you to utilise the library's output capabilities.
```python
from smart_pdf_for_business import PDFDoc

# Load a PDF
pdf = PDFDoc.from_file("example.pdf")

# Perform semantic search
clauses = pdf.search_by_meaning("termination clause", chunk_by="semantic")

# Export results
clauses.to_csv("output.csv")
clauses.to_excel("output.xlsx")
```
Alternatively, you can use `as_tuple=True` to return the result as a tuple.
```python
from smart_pdf_for_business import PDFDoc

# Load a PDF
pdf = PDFDoc.from_file("example.pdf")

# Perform semantic search
clauses = pdf.search_by_meaning("termination clause", chunk_by="semantic", as_tuple=True)

# Print result as tuple
print(clauses)
```


## 📚 API

### <kbd>class</kbd> PDFDoc
| Attribute | Description |
|------|-------------|
| `data: bytes` | Raw byte content of the PDF document. |
| `path: Optional[Path]` | File system path to the PDF file, if loaded from disk. |
| `name: Optional[str]` | Name of the PDF document (usually the filename). |
| `spacy_doc: Optional[Doc]` | Processed spaCy Doc object, containing text, layout, and markdown. |
| `sections: List[Tuple[str, str]]` | List of `(title, body)` tuples extracted from the document. |
| `weighted_sections: List[Tuple[Tuple[str, str], float]]` | List of sections paired with a semantic match weight. |
| `signatures: List[Signature]` | Detected signatures stored as `Signature` objects. |

---

| Methods | Description | Parameter |
|---------|-------------|-----------|
| `from_file` | Creates a `PDFDoc` from a PDF file. <br>**Return:** `PDFDoc` | `path: str \| Path` <br>- Path to the PDF file |
| `from_folder` | Loads all PDFs from a folder (optionally recursively). <br>**Return:** `list[PDFDoc]` | `folder_path: str \| Path` <br>- Folder containing PDFs <br>`recursive: bool = True` <br>- Include subfolders |
| `from_bytes` | Creates a `PDFDoc` from raw PDF byte content. <br>**Return:** `PDFDoc` | `data: bytes` <br>- PDF bytes <br>`name: Optional[str] = None` <br>- Name assigned to document |
| `from_byte_list` | Creates multiple `PDFDoc` objects from PDF byte streams. <br>**Return:** `list[PDFDoc]` | `byte_list: List[bytes]` <br>- List of PDF byte streams <br>`names: Optional[List[str]] = None` <br>- Corresponding PDF names |
| `search_signature` | Detects signatures near keyword regions and optionally saves cropped images. Updates `self.signatures`. <br>**Return:** `PDFDoc` | `keywords: list[str]` <br>- Signature-related keywords <br>`exact=False` <br>- Forbid substring matching <br>`max_distance=70` <br>- Max pixel distance <br>`save_folder=None` <br>- Folder to save crops <br>`min_contrast=30` <br>- Minimum image contrast <br>`filter_stroke_density=True` <br>- Stroke-density filtering <br>`enforce_text_type: bool = True` <br>- Filter signature text using nlp  |
| `search_header` | Searches section headers for keyword matches. <br>**Return:** `PDFDoc` or `list[tuple[str, str]]` | `keywords: list[str]` <br>- Header keywords <br>`exact: bool = True` <br>- Exact match <br>`as_tuple: bool = False` <br>- Return tuples |
| `search_body` | Searches section bodies for keyword matches. <br>**Return:** `PDFDoc` or `list[tuple[str, str]]` | `keywords: list[str]` <br>- Body keywords <br>`exact: bool = True` <br>- Exact match <br>`as_tuple: bool = False` <br>- Return tuples |
| `search_by_meaning` | Performs semantic search across sections, sentences, paragraphs, or words. <br>**Return:** `PDFDoc` or `list[tuple[str, float]]` | `query: str` <br>- Search query <br>`threshold: float = 0` <br>- Minimum similarity <br>`chunk_by: str = "section"` <br>- Chunking strategy <br>`as_tuple: bool = False` <br>- Return raw tuples <br>`word_count: int = 5` <br>- Words per chunk <br>`buffer_size: int = 1` <br>- Chunk overlap <br>`chunk_text_semantically_threshold: float = 0.3` <br>- Semantic chunk threshold <br>`max_results: int = 5` <br>- Max results |
| `to_text` | Converts the PDF to plain text with optional signature annotations. <br>**Return:** `str` | `annotate_signatures: bool = True` <br>- Annotate signature positions |
| `to_markdown` | Converts the PDF to Markdown with optional signature annotations. <br>**Return:** `str` | `annotate_signatures: bool = True` <br>- Annotate signature positions |
| `to_dataframe` | Converts the document to a structured pandas DataFrame. <br>**Return:** `pandas.DataFrame` | None |
| `to_excel` | Exports the document DataFrame to an Excel (.xlsx) file. <br>**Return:** `None` | `path: str \| Path` <br>- Output .xlsx path <br>`sheet_name: str = "Sheet1"` <br>- Sheet name |
| `to_csv` | Exports the document DataFrame to a CSV file. <br>**Return:** `None` | `path: str \| Path` <br>- Output CSV file path |
| `to_json` | Serializes the document into JSON, optionally writing to a file. <br>**Return:** `str` (JSON) or `None` (if saved to file) | `path: Optional[str \| Path] = None` <br>- Optional save path <br>`indent: int = 2` <br>- JSON formatting |

### <kbd>class</kbd> PDFDocBatch
| Attribute | Description |
|-----------|-------------|
| `pdfdocs: list[PDFDoc]` | List containing all `PDFDoc` instances in the batch. |
---
| Methods | Description | Parameter |
|---------|-------------|-----------|
| `from_folder` | Creates a batch from all PDFs in a folder. <br>**Return:** `PDFDocBatch` | `path: str \| Path` <br>- Path to the folder containing PDFs <br>`recursive: bool = True` <br>- Whether to include subfolders |
| `from_byte_list` | Creates a batch from a list of PDF byte streams. <br>**Return:** `PDFDocBatch` | `byte_list: List[bytes]` <br>- List of PDF bytes <br>`names: Optional[List[str]] = None` <br>- Optional list of names corresponding to each PDF |
| `from_pdfdoc_list` | Creates a batch from an existing list of `PDFDoc` objects. <br>**Return:** `PDFDocBatch` | `pdfdoc_list: List[PDFDoc]` <br>- List of `PDFDoc` instances |
| `extend` | Extends the batch with another batch or list of PDFs. <br>**Return:** `None` | `other: Union[List[PDFDoc], PDFDocBatch]` <br>- Batch or list of PDFs to append |
| `append` | Appends a single `PDFDoc` to the batch. <br>**Return:** `None` | `pdfdoc: PDFDoc` <br>- `PDFDoc` instance to append |
| `search_signature` | Detects handwritten or scanned signatures associated with keyword regions for multiple PDFs. <br>**Return:** `PDFDocBatch` | `keywords: List[str]` <br>- Keywords used to locate signature-related regions <br>`exact: bool = False` <br>- Whether keyword matching must be exact <br>`max_distance: int = 70` <br>- Maximum pixel distance between a keyword block and signature <br>`save_folder: Optional[str \| Path] = None` <br>- Folder to save cropped signature images, if provided <br>`min_contrast: int = 30` <br>- Minimum pixel contrast threshold <br>`filter_stroke_density: bool = True` <br>- Filter image regions based on stroke density <br>`enforce_text_type: bool = True` <br>- Filter signature text based on stroke density |
| `search_header` | Searches headers in every PDF for keywords. <br>**Return:** `PDFDocBatch` | `keywords: list[str]` <br>- Header keywords <br>`exact: bool = True` <br>- Exact or partial matching |
| `search_body` | Searches body text in every PDF for keywords. <br>**Return:** `PDFDocBatch` | `keywords: list[str]` <br>- Body keywords <br>`exact: bool = True` <br>- Exact or partial matching |
| `search_by_meaning` | Performs semantic search across all PDFs. <br>**Return:** `PDFDocBatch` | `query: str` <br>- Natural language query <br>`threshold: float = 0` <br>- Min similarity score <br>`chunk_by: str = "section"` <br>- Chunking method <br>`word_count: int = 5` <br>- Words per chunk <br>`buffer_size: int = 1` <br>- Overlap size <br>`chunk_text_semantically_threshold: float = 0.3` <br>- Semantic similarity threshold <br>`max_results: int = 5` <br>- Max results per PDF |
| `to_dataframe` | Combines all PDFs in the batch into a DataFrame. PDFs with the same name overwrite each other. <br>**Return:** `pandas.DataFrame` | None |
| `to_excel` | Exports batch data to an Excel file. <br>**Return:** `None` | `path: str \| Path` <br>- Output Excel path <br>`sheet_name: str = "Sheet1"` <br>- Sheet name |
| `to_csv` | Exports batch data to a CSV file. <br>**Return:** `None` | `path: str \| Path` <br>- Output CSV file path |

### <kbd>dataclass</kbd> Signature

| Attribute  | Description                               |
| ---------- | ----------------------------------------- |
| `keyword`  | Keyword used for search                   |
| `text`     | OCR text of signature region              |
| `bbox`     | Bounding box coordinates (x1, y1, x2, y2) |
| `page`     | Page number                               |
| `img`      | Cropped image as `numpy.ndarray`          |
| `distance` | Distance to keyword                       |
---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---
