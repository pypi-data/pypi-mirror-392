from pathlib import Path
from smart_pdf_for_business import PDFDoc

report = PDFDoc.from_file(Path(__file__).parent / "testPdf" / "signature" / "test1.pdf")
sig = report.search_signature(["Created By", "Endorsed By", "Approved By"] , save_folder="examples/signature/test1")
print(report.to_text())