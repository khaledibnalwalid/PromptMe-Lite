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

# Resume storage
resume_map = {}  # {index: resume_dict}
resume_count = 0
MAX_RESUMES = 1000  # Allow up to 1000 resume submissions for stress testing


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


def add_resume(resume: dict):
    """
    Add a resume to the vector store.

    Resume format:
    {
        "name": str,
        "email": str,
        "experience": str,
        "skills": str
    }

    Args:
        resume: Resume dictionary
    """
    global resume_count

    # Prevent unbounded growth
    if resume_count >= MAX_RESUMES:
        raise ValueError("Resume database is full. Please contact HR to clear old entries.")

    # Create embedding text from resume (name + experience + skills)
    # This is what gets embedded for semantic search
    embedding_text = f"{resume['name']} {resume['experience']} {resume['skills']}"

    # Encode and add to FAISS
    vec = encode_text(embedding_text)
    index.add(np.array(vec, dtype=np.float32))

    # Store full resume
    resume_map[resume_count] = resume
    resume_count += 1


def search_similar(query: str, k: int = 3, limit_to_latest: int = None):
    """
    Search for similar resumes in the vector store.

    Args:
        query: Query string (e.g., "Find candidates with Python experience")
        k: Number of results to return
        limit_to_latest: If specified, only search within the latest N resumes (for performance)

    Returns:
        List of resume dictionaries
    """
    if resume_count == 0:
        return []

    # Encode query
    q_vec = encode_text(query)

    # If limit_to_latest is specified, only search recent resumes
    if limit_to_latest and resume_count > limit_to_latest:
        # Create a temporary FAISS index with only the latest N resumes
        start_idx = resume_count - limit_to_latest
        temp_index = faiss.IndexFlatL2(EMBEDDING_DIM)

        # Add vectors for latest resumes only
        for i in range(start_idx, resume_count):
            if i in resume_map:
                resume = resume_map[i]
                embedding_text = f"{resume['name']} {resume['experience']} {resume['skills']}"
                vec = encode_text(embedding_text)
                temp_index.add(np.array(vec, dtype=np.float32))

        # Search in temp index
        D, I = temp_index.search(np.array(q_vec, dtype=np.float32), min(k, limit_to_latest))

        # Map indices back to original resume_map indices
        results = []
        for idx in I[0]:
            if idx != -1:
                original_idx = start_idx + idx
                if original_idx in resume_map:
                    results.append(resume_map[original_idx])
    else:
        # Search all resumes (existing behavior)
        D, I = index.search(np.array(q_vec, dtype=np.float32), min(k, resume_count))

        # Retrieve resumes
        results = []
        for idx in I[0]:
            if idx != -1 and idx in resume_map:
                results.append(resume_map[idx])

    return results


def get_all_resumes():
    """
    Get all resumes in the database.

    Returns:
        List of all resume dictionaries
    """
    return list(resume_map.values())


def clear_vector_store():
    """Clear all resumes from the vector store."""
    global index, resume_map, resume_count
    # Re-initialize the index
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    resume_map.clear()
    resume_count = 0
