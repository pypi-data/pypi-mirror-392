from pathlib import Path
from smart_pdf_for_business import PDFDoc

report = PDFDoc.from_file(Path(__file__).parent / "testPdf" / "article" / "Bai_Re-Ranking_via_Metric_Fusion_for_Object_Retrieval_and_Person_Re-Identification_CVPR_2019_paper.pdf")
result1 = report.search_header(["abstract"])
print(result1.to_text())
print(result1.to_json())
print(result1)
print(result1.to_dataframe())
