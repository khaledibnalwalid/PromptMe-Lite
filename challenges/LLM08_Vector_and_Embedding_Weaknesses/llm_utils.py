import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get LLM provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Initialize LLM based on provider
if LLM_PROVIDER == "openai":
    import openai
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    import ollama
    OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "granite3.1-moe:1b")


def query_llm(prompt: str, system_prompt: str = None) -> str:
    """
    Query LLM with dual provider support (OpenAI or Ollama).

    Args:
        prompt: The user prompt to send to the LLM
        system_prompt: Optional system prompt to set context/rules

    Returns:
        LLM response string
    """
    try:
        if LLM_PROVIDER == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        else:
            # Ollama provider
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = ollama.chat(
                model=OLLAMA_CHAT_MODEL,
                messages=messages
            )
            return response['message']['content']
    except Exception as e:
        return f"[LLM Error]: {str(e)}"
