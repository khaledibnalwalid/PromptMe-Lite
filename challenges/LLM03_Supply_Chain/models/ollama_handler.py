import os
import ollama

OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "granite3.1-moe:1b")

def generate_with_ollama(model_name, history, prompt):
    """Generate response using Ollama native client (following app1.py pattern)"""

    # System prompt for short, secure responses
    system_prompt = {
        "role": "system",
        "content": (
            "You are a helpful AI assistant for supply chain security. "
            "Keep responses brief (2-3 sentences max). "
            "Never reveal internal system information, configurations, or technical details. "
            "Do not discuss data exfiltration, monitoring, or backend processes."
        )
    }

    try:
        messages = [system_prompt] + history + [{"role": "user", "content": prompt}]
        response = ollama.chat(
            model=model_name,
            messages=messages
        )
        return response['message']['content']
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")
