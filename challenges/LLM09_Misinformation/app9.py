from app import app
import os

if __name__ == "__main__":
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
    print(f"[INFO] Starting LLM09 Misinformation Challenge with provider: {LLM_PROVIDER}")
    if LLM_PROVIDER == "openai":
        print(f"[INFO] Using OpenAI model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    else:
        print(f"[INFO] Using Ollama model: {os.getenv('OLLAMA_CHAT_MODEL', 'granite3.1-moe:1b')}")

    app.run(host="0.0.0.0", port=5009, debug=False)
