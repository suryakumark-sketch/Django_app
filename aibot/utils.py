""" Utils for Aibot app."""

import docx
import PyPDF2

def extract_text(file):
    """ Extract text from a file."""
    name = file.name.lower()

    if name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    return ""
