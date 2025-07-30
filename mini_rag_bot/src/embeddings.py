import os
import warnings

# Suppress the deprecation warning for HuggingFaceEmbeddings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_community.embeddings")

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    print("✅ Using langchain_huggingface.HuggingFaceEmbeddings")
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print("⚠️ Using langchain_community.embeddings.HuggingFaceEmbeddings (consider upgrading to langchain-huggingface)")

def get_embedding_function():
    """Return the embedding function."""
    print("🔧 Initializing HuggingFace embeddings model...")
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
