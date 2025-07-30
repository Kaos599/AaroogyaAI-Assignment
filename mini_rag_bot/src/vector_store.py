import chromadb
import os

# Disable ChromaDB telemetry to fix the capture() error
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

# Also set it programmatically for the current session
import chromadb.config
chromadb.config.Settings.anonymized_telemetry = False

def get_chroma_client():
    """Return a ChromaDB client with telemetry disabled."""
    print("🔧 Initializing ChromaDB client...")
    client = chromadb.PersistentClient(
        path="db/",
        settings=chromadb.config.Settings(
            anonymized_telemetry=False
        )
    )
    print("✅ ChromaDB client initialized successfully")
    return client

def create_collection(client, name="women_health"):
    """Create a new collection or get an existing one."""
    print(f"🔧 Creating/accessing collection: {name}")
    collection = client.get_or_create_collection(name)
    print(f"✅ Collection '{name}' ready")
    return collection

def add_documents_to_collection(collection, documents, embedding_function):
    """Add documents to a collection with proper logging."""
    if not documents:
        print("⚠️ No documents to add to collection")
        return
    
    print(f"🔧 Adding {len(documents)} documents to collection...")
    
    # Generate embeddings
    print("🔧 Generating embeddings...")
    embeddings = embedding_function.embed_documents([doc.page_content for doc in documents])
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # Add to collection
    collection.add(
        embeddings=embeddings,
        documents=[doc.page_content for doc in documents],
        metadatas=[doc.metadata for doc in documents],
        ids=[f"{doc.metadata.get('source', 'unknown')}_{i}" for i, doc in enumerate(documents)]
    )
    print(f"✅ Successfully added {len(documents)} documents to collection")
