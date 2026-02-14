import os
import ollama

OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "granite3.1-moe:1b")

def generate_with_ollama(model_name, history, prompt):
    """Generate response using Ollama native client (following app1.py pattern)"""
    try:
        response = ollama.chat(
            model=model_name,
            messages=history + [{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")
