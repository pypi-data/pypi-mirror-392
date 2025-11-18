import requests
from smart_pdf_for_business import PDFDoc

if __name__ == "__main__":
    url = "https://drive.google.com/uc?export=download&id=1nXtm261dVrHTLuWv0_VLuO0kfhk17PYT"


    response = requests.get(url)
    response.raise_for_status()

    file_bytes = response.content
    report = PDFDoc.from_bytes(file_bytes)
    result1 = report.search_header(["abstract"])
    print(result1)