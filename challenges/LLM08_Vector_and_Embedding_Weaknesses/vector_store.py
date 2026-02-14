import os
import numpy as np
import faiss
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get embedding provider configuration
EMBEDDING_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Initialize embedding model based on provider
if EMBEDDING_PROVIDER == "openai":
    # Use OpenAI embeddings
    import openai
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIM = 1536  # text-embedding-3-small dimension
else:
    # Use Ollama embeddings
    import ollama
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    EMBEDDING_DIM = 768  # nomic-embed-text dimension

# Initialize FAISS index
index = faiss.IndexFlatL2(EMBEDDING_DIM)

doc_map = {}
doc_count = 0


def encode_text(text: str) -> np.ndarray:
    """
    Encode text to embedding vector using configured provider.

    Args:
        text: Text to encode

    Returns:
        Embedding vector as numpy array
    """
    if EMBEDDING_PROVIDER == "openai":
        response = openai_client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=text
        )
        embedding = response.data[0].embedding
        return np.array([embedding], dtype=np.float32)
    else:
        # Ollama embeddings
        response = ollama.embeddings(
            model=OLLAMA_EMBEDDING_MODEL,
            prompt=text
        )
        embedding = response['embedding']
        return np.array([embedding], dtype=np.float32)


def search_similar(query: str, k: int = 2):
    """
    Search for similar documents in the vector store.

    Args:
        query: Query string
        k: Number of results to return

    Returns:
        List of similar documents
    """
    if doc_count == 0:
        return []

    q_vec = encode_text(query)
    D, I = index.search(np.array(q_vec, dtype=np.float32), k)

    # Filter out -1 and non-existent keys
    results = []
    for idx in I[0]:
        if idx != -1 and idx in doc_map:
            results.append(doc_map[idx])

    return results


def add_document(text: str):
    """
    Add a document to the vector store.

    Args:
        text: Document text to add
    """
    global doc_count
    vec = encode_text(text)
    index.add(np.array(vec, dtype=np.float32))
    doc_map[doc_count] = text
    doc_count += 1


def clear_vector_store():
    """Clear all documents from the vector store."""
    global index, doc_map, doc_count
    # Re-initialize the index and document map
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    doc_map.clear()
    doc_count = 0
