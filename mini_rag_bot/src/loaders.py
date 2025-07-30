import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.docstore.document import Document

def load_pdf(file_path):
    """Load a PDF file and return a list of Document objects."""
    loader = PyPDFLoader(file_path)
    return loader.load()

def load_html(url):
    """Load an HTML document from a URL and return a list of Document objects."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        metadata = {"source": url}
        return [Document(page_content=text, metadata=metadata)]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
