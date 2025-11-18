from pathlib import Path
from smart_pdf_for_business import PDFDocBatch

reports = PDFDocBatch.from_folder(Path(__file__).parent / "testPdf" / "article")
result1 = reports.search_header(["abstract"])
result2 = reports.search_body(["limitations"])
result3 = reports.search_by_meaning("who wrote this report?", chunk_by="semantic", threshold=0.1)
for i, v in enumerate([report for report in reports]):
    print("--------------------------------")
    print(v.name)
    print("--------------ABTRACT SEARCH------------------")
    print(result1[i].to_text())
    print("------------LIMITATION SEARCH--------------------")
    print(result2[i].to_text())
    print("-------------who wrote this report?-------------------")
    print(result3[i].to_text())
    print("--------------------------------")