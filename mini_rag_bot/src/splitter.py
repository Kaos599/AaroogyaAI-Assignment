from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text(documents):
    """Split a list of documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_documents(documents)
