import os
import sys

sys.path.append(os.path.abspath(os.curdir))

from bs4 import BeautifulSoup  # noqa: E402

from jarvys_dev.tools import memory  # noqa: E402

USAGE = f"Usage: python {os.path.basename(sys.argv[0])} <path_to_linkedin_profile.html_or_pdf>"


def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError("Missing PyMuPDF dependency. Please install it using 'pip install PyMuPDF'.")
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_html(html_path: str) -> str:
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        text = soup.get_text(separator="\n")
        return text


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        sys.exit(1)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        content = extract_text_from_pdf(path)
    elif ext in [".html", ".htm"]:
        content = extract_text_from_html(path)
    else:
        print("Unsupported file format. Use PDF or HTML.")
        sys.exit(1)
    content = content.strip()
    if not content:
        print("No text extracted from LinkedIn profile.")
        sys.exit(1)
    try:
        doc_id = memory.upsert_embedding(content)
        print(f"\u2705 LinkedIn profile imported with ID: {doc_id}")
    except Exception as e:
        print(f"\u274c Failed to insert into vector DB: {e}")
