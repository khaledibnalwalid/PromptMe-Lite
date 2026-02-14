import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from main .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get configuration from .env
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Import handlers based on provider
if LLM_PROVIDER == "openai":
    from .openai_handler import generate_with_openai
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Model registry for OpenAI
    MODEL_REGISTRY = {
        OPENAI_MODEL: "openai",
        "custom": "rogue"
    }
elif LLM_PROVIDER == "ollama":
    from .ollama_handler import generate_with_ollama
    OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "granite3.1-moe:1b")

    # Model registry for Ollama
    MODEL_REGISTRY = {
        OLLAMA_CHAT_MODEL: "ollama",
        "custom": "rogue"
    }
else:
    raise ValueError(f"Invalid LLM_PROVIDER: {LLM_PROVIDER}. Must be 'ollama' or 'openai'")

# Always import rogue handler (used by both providers)
from .rogue_handler import generate_with_rogue

def generate_response(model_name, history, prompt, session_id=None):
    """Generate response using the configured LLM provider"""
    backend = MODEL_REGISTRY.get(model_name)

    if backend == "openai":
        return generate_with_openai(model_name, history, prompt)
    elif backend == "ollama":
        return generate_with_ollama(model_name, history, prompt)
    elif backend == "rogue":
        return generate_with_rogue(history, prompt, session_id)
    else:
        raise ValueError("Unknown model")
