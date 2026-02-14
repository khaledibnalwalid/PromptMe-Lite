import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from main .env file
env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Conditional imports based on provider
if LLM_PROVIDER == "openai":
    import openai
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    import ollama
    OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "granite3.1-moe:1b")

def query_llm(prompt):
    """
    Query LLM with dual provider support (OpenAI or Ollama).

    Args:
        prompt: The prompt to send to the LLM

    Returns:
        LLM response string
    """
    try:
        if LLM_PROVIDER == "openai":
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        else:
            # Use Ollama
            response = ollama.chat(
                model=OLLAMA_CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
    except Exception as e:
        return f"[LLM Error]: {str(e)}"
