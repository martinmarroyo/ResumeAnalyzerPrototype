"""A collection of functions used for processing files"""
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

def get_pdf(path: str) -> Document:
    loader = PyMuPDFLoader(path)
    return loader.load()[0]


def get_text_file(path: str) -> Document:
    with open(path, "r") as f:
        text = f.read()
    
    return Document(page_content=text, metadata={"source": path})


def load_file_from_path(path: str) -> Document:
    if path.endswith("pdf"):
        doc = get_pdf(path)
    else:
        doc = get_text_file(path)
    
    return doc
