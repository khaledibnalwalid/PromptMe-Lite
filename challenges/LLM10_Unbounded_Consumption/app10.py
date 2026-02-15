from flask import Flask, render_template, request, session
import os
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get LLM provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

app = Flask(__name__)
app.secret_key = "S3cr3t_K3y_LLM10_Unb0und3d"
app.config['SESSION_PERMANENT'] = False

# Hidden system instruction
system_prompt = """You are a helpful and ethical AI assistant."""

FLAG = "flag{R3$0urC3_ExH@us7!0N_D37EcTeD}"
TIME_THRESHOLD = 90.0      # seconds
TOKEN_THRESHOLD = 400     # approximate words

def generate_response(user_input):
    """
    Generate response using configured LLM provider.
    NO rate limiting or input validation - this is intentionally vulnerable for DoS testing.
    """
    start = time.time()

    try:
        if LLM_PROVIDER == "openai":
            import openai
            OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            response_text = response.choices[0].message.content
        else:
            # Use Ollama with LangChain
            from langchain_ollama import ChatOllama
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

            OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "granite3.1-moe:1b")
            OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

            model = ChatOllama(model=OLLAMA_CHAT_MODEL, base_url=OLLAMA_URL)
            system_message = SystemMessagePromptTemplate.from_template(system_prompt)
            prompt = HumanMessagePromptTemplate.from_template(user_input)
            chat_history = [system_message, prompt]
            chat_template = ChatPromptTemplate.from_messages(chat_history)
            chain = chat_template | model | StrOutputParser()

            response_text = chain.invoke({})

    except Exception as e:
        response_text = f"[!] Error while generating response: {str(e)}"

    end = time.time()
    elapsed = end - start
    return response_text, elapsed

@app.route("/", methods=["GET"])
def index():
    # Clear session on page load to ensure fresh start
    session.clear()
    return render_template("index.html", response_text=None, user_input=None)

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form["message"]
    response, elapsed = generate_response(user_input)

    print(f"[DEBUG] Full response length: {len(response)}")
    print(f"[DEBUG] Response preview: {response[:300]}...")

    word_count = len(response.split())
    print(f"[DEBUG] Word count: {word_count} | Time taken: {elapsed:.2f}s")

    time_info = f"\n\n[Time taken: {elapsed:.2f} seconds]"

    flag_message = ""

    # DoS detection - the CTF challenge!
    if elapsed > TIME_THRESHOLD and word_count > TOKEN_THRESHOLD:
        flag_message += f'\n<span class="flag">[!] Potential DoS detected. FLAG: {FLAG}</span>'
        print("[!] FLAG triggered.")

    return render_template("index.html", response_text=response + flag_message, user_input=user_input)

@app.route("/reset", methods=["POST"])
def reset():
    """Reset session - clear all session data"""
    session.clear()
    return "", 200

if __name__ == "__main__":
    # Print provider info
    print(f"[INFO] Starting LLM10 Unbounded Consumption Challenge with provider: {LLM_PROVIDER}")
    if LLM_PROVIDER == "openai":
        print(f"[INFO] Using OpenAI model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    else:
        print(f"[INFO] Using Ollama model: {os.getenv('OLLAMA_CHAT_MODEL', 'granite3.1-moe:1b')}")

    print("[WARNING] No rate limiting or input validation - INTENTIONALLY VULNERABLE for DoS testing")

    app.run("0.0.0.0", debug=False, port=5010)
