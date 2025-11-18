from pathlib import Path
from smart_pdf_for_business import PDFDoc

report = PDFDoc.from_file(Path(__file__).parent / "testPdf" / "article" / "Bai_Re-Ranking_via_Metric_Fusion_for_Object_Retrieval_and_Person_Re-Identification_CVPR_2019_paper.pdf")
result1 = report.search_header(["abstract"], as_tuple=True)
print(result1)
result2 = report.search_body(["limitations"], as_tuple=True)
print(result2)
result3 = report.search_by_meaning("who wrote this report?", as_tuple=True, chunk_by="semantic")
print(result3)