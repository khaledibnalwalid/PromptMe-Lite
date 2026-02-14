from flask import Flask, render_template, request, session
import os
import time
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
    from langchain_ollama import ChatOllama
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
    OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "granite3.1-moe:1b")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = ChatOllama(model=OLLAMA_CHAT_MODEL, base_url=OLLAMA_URL)
    system_message = SystemMessagePromptTemplate.from_template("You are a helpful and ethical AI assistant.")

app = Flask(__name__)
app.secret_key = "S3cr3t_K3y_LLM10_Unb0und3d"
app.config['SESSION_PERMANENT'] = False

# Constants
FLAG = "flag{R3$0urC3_ExH@us7!0N_D37EcTeD}"
TIME_THRESHOLD = 90.0      # seconds
TOKEN_THRESHOLD = 400     # approximate words

def generate_response(user_input):
    """Generate response using configured LLM provider"""
    start = time.time()

    try:
        if LLM_PROVIDER == "openai":
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful and ethical AI assistant."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            response_text = response.choices[0].message.content
        else:
            # Use Ollama with LangChain
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
    # Initialize session if not exists
    if "messages" not in session:
        session["messages"] = []
    if "query_count" not in session:
        session["query_count"] = 0

    return render_template("index.html",
                          response_text=None,
                          user_input=None,
                          messages=session.get("messages", []),
                          query_count=session.get("query_count", 0))

@app.route("/ask", methods=["POST"])
def ask():
    # Initialize session if not exists
    if "messages" not in session:
        session["messages"] = []
    if "query_count" not in session:
        session["query_count"] = 0

    # Rate limiting: max 20 queries per session
    query_count = session.get("query_count", 0)
    if query_count >= 20:
        return render_template("index.html",
                             response_text="⛔ Rate limit exceeded. Maximum 20 queries per session. Please refresh the page.",
                             user_input="",
                             messages=session.get("messages", []),
                             query_count=query_count), 429

    user_input = request.form.get("message", "").strip()

    # Input validation
    if not user_input:
        return render_template("index.html",
                             response_text="Please provide a message",
                             user_input="",
                             messages=session.get("messages", []),
                             query_count=query_count), 400

    if len(user_input) > 5000:
        return render_template("index.html",
                             response_text="Message too long (max 5000 characters)",
                             user_input=user_input,
                             messages=session.get("messages", []),
                             query_count=query_count), 400

    response, elapsed = generate_response(user_input)

    print(f"[DEBUG] Full response length: {len(response)}")
    print(f"[DEBUG] Response preview: {response[:300]}...")

    word_count = len(response.split())
    print(f"[DEBUG] Word count: {word_count} | Time taken: {elapsed:.2f}s")

    time_info = f"\n\n[Time taken: {elapsed:.2f} seconds]"

    flag_message = ""

    # DoS detection - the CTF vulnerability!
    if elapsed > TIME_THRESHOLD and word_count > TOKEN_THRESHOLD:
        flag_message += f'\n<span class="flag">[!] Potential DoS detected. FLAG: {FLAG}</span>'
        print("[!] FLAG triggered.")

    # Add messages to session history
    session["messages"].append({"role": "user", "content": user_input})
    session["messages"].append({"role": "assistant", "content": response + flag_message})

    # Limit message history to last 200 messages
    if len(session["messages"]) > 200:
        session["messages"] = session["messages"][-200:]

    # Increment query counter
    session["query_count"] = query_count + 1
    session.modified = True

    return render_template("index.html",
                          response_text=response + flag_message,
                          user_input=user_input,
                          messages=session.get("messages", []),
                          query_count=session.get("query_count", 0))

@app.route("/reset", methods=["POST"])
def reset():
    """Reset session - clear messages and query counter"""
    session.clear()
    return "", 200

if __name__ == "__main__":
    # Print provider info
    print(f"[INFO] Starting LLM10 Unbounded Consumption Challenge with provider: {LLM_PROVIDER}")
    if LLM_PROVIDER == "openai":
        print(f"[INFO] Using OpenAI model: {OPENAI_MODEL}")
    else:
        print(f"[INFO] Using Ollama model: {OLLAMA_CHAT_MODEL}")

    app.run("0.0.0.0", debug=False, port=5010)
