"""A collection of functions used for processing files"""
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
import os 

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


def delete_file(file_path: str):
        """
        Delete a file from the filesystem.

        Parameters:
        - file_path: str : The path to the file to be deleted
        """
        try:
            os.remove(file_path)
            print(f"File {file_path} successfully deleted")
        except FileNotFoundError:
            print(f"File {file_path} not found")
        except PermissionError:
            print(f"Permission denied: Unable to delete {file_path}")
        except Exception as e:
            print(f"Error occurred while deleting the file: {e}")