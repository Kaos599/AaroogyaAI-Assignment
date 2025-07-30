import os
import argparse
from .loaders import load_pdf, load_html
from .splitter import split_text
from .vector_store import get_chroma_client, create_collection, add_documents_to_collection
from .embeddings import get_embedding_function
from .retriever import Retriever
from .generator import generate_answer
from .translator import translate_to_english, translate_from_english

def ingest_documents(file_path, url):
    """Ingest documents from a file or URL."""
    if file_path:
        documents = load_pdf(file_path)
    elif url:
        documents = load_html(url)
    else:
        return

    chunks = split_text(documents)
    client = get_chroma_client()
    collection = create_collection(client)
    embedding_function = get_embedding_function()
    add_documents_to_collection(collection, chunks, embedding_function)
    print("Documents ingested successfully.")

def ask_question(question, lang='en'):
    """Ask a question and get an answer."""
    if lang != 'en':
        question = translate_to_english(question, lang)

    retriever = Retriever()
    context_docs = retriever.query(question)

    # Create a list of Document objects for the generator
    context = [doc for doc in context_docs]

    result = generate_answer(context, question)

    if lang != 'en':
        result['answer'] = translate_from_english(result['answer'], lang)

    print("Answer:", result['answer'])
    print("Citations:", result['citations'])

def main():
    """Main function to run the RAG bot."""
    parser = argparse.ArgumentParser(description="Mini RAG Bot for Women's Health FAQs")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument("--file", help="Path to a PDF file")
    ingest_parser.add_argument("--url", help="URL of an HTML document")

    ask_parser = subparsers.add_parser("ask", help="Ask a question")
    ask_parser.add_argument("question", help="The question to ask")
    ask_parser.add_argument("--lang", default="en", help="Language of the question (e.g., 'hi' for Hindi)")

    args = parser.parse_args()

    if args.command == "ingest":
        if not args.file and not args.url:
            print("Please provide either a file or a URL to ingest.")
            return
        ingest_documents(args.file, args.url)
    elif args.command == "ask":
        # Set dummy API keys if not provided, for local testing without actual API calls
        if "GEMINI_API_KEY" not in os.environ:
            os.environ["GEMINI_API_KEY"] = "dummy_key"
        if "TAVILY_API_KEY" not in os.environ:
            os.environ["TAVILY_API_KEY"] = "dummy_key"
        ask_question(args.question, args.lang)

if __name__ == "__main__":
    main()
