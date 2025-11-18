from pathlib import Path
from smart_pdf_for_business import PDFDocBatch

reports = PDFDocBatch.from_folder(Path(__file__).parent / "testPdf" / "article")
result1 = reports.search_header(["abstract"])
result2 = reports.search_body(["method"])
print(result1.to_dataframe())
print(result2.to_dataframe())
result3 = result1 + result2
print(result3.to_dataframe())