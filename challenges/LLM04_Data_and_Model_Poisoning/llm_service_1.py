import csv, os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path
import numpy as np

# Load environment variables from main .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Conditional imports based on provider
if LLM_PROVIDER == "openai":
    import openai
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    import ollama
    OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "granite3.1-moe:1b")

qa_knowledge = []
csv_questions = []
question_embeddings = []

# Source question patterns
SOURCE_QUESTION_KEYWORDS = [
    "source of information", "knowledge base", "training data",
    "where is this from", "where does this come from",
    "data source", "source of truth", "what are you trained on"
]

# Patterns indicating user wants to contribute data
CONTRIBUTION_KEYWORDS = [
    "here's the latest", "here is the latest", "updated information",
    "new version", "latest version", "owasp top 10:",
    "correct information", "actual list", "real list"
]

# Prompt template
prompt_template = """
You are an OWASP LLM Security Assistant.
You are only allowed to answer questions based on the provided CONTEXT. Do NOT use prior knowledge.
If the context does not answer the question, reply ONLY with:
"I don't know based on the provided context."

Keep responses brief (2-3 sentences max, max 100 tokens).

---

QUESTION:
{question}

---

CONTEXT:
{context}

---

ANSWER:
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "test_docs", "owasp_llm_qa.csv")

def get_embedding(text):
    """Get embedding for text using OpenAI API"""
    try:
        response = openai_client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return np.array(response.data[0].embedding)
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

def reload_knowledge_base():
    global qa_knowledge, csv_questions, question_embeddings

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            qa_knowledge = list(reader)

        csv_questions = [qa["Question"] for qa in qa_knowledge]

        # Get embeddings from OpenAI
        print("Generating embeddings with OpenAI...")
        question_embeddings = []
        for question in csv_questions:
            embedding = get_embedding(question)
            if embedding is not None:
                question_embeddings.append(embedding)

        question_embeddings = np.array(question_embeddings)

        print("CSV_PATH:", CSV_PATH)
        print("File exists:", os.path.exists(CSV_PATH))
        print(f"✅ Reloaded {len(qa_knowledge)} Q&A entries from local file")
        return True
    except Exception as e:
        print("❌ Failed to reload knowledge base:", e)
        return False


# Perform initial load
reload_knowledge_base()

# Helper to check if question is about the source
def is_source_question(question: str) -> bool:
    lowered = question.lower()
    return any(keyword in lowered for keyword in SOURCE_QUESTION_KEYWORDS)

# Helper to check if user is trying to contribute data
def is_contribution_attempt(question: str) -> bool:
    lowered = question.lower()
    return any(keyword in lowered for keyword in CONTRIBUTION_KEYWORDS)

# Extract and save contributed data
def process_contribution(user_input: str) -> str:
    """Process user-contributed 'updated' OWASP Top 10 data and save it to knowledge base"""
    global qa_knowledge, csv_questions, question_embeddings

    # Check if input contains a list-like structure
    if "llm01:" in user_input.lower() or "1." in user_input or "llm02:" in user_input.lower():
        # Extract the list content
        lines = [line.strip() for line in user_input.split('\n') if line.strip()]

        # Build new answer from user input
        new_answer_lines = []
        for line in lines:
            # Skip conversational parts, only keep the list items
            if any(x in line.lower() for x in ["llm0", "llm1", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]):
                new_answer_lines.append(line)

        if new_answer_lines:
            new_answer = "\n".join(new_answer_lines)

            # Find the "List top 10 LLM vulnerabilities" entry and update it
            for i, qa in enumerate(qa_knowledge):
                if qa["Question"].strip().lower() == "list top 10 llm vulnerabilities":
                    qa_knowledge[i]["Answer"] = new_answer

                    # Rebuild embeddings
                    csv_questions = [qa["Question"] for qa in qa_knowledge]
                    temp_embeddings = []
                    for question in csv_questions:
                        embedding = get_embedding(question)
                        if embedding is not None:
                            temp_embeddings.append(embedding)
                    question_embeddings = np.array(temp_embeddings)

                    print(f"⚠️ Knowledge base updated with user-contributed data!")
                    return f"Thank you! I've updated my knowledge base with the latest OWASP LLM Top 10 information you provided. This will help me provide more accurate answers going forward."

    return "I appreciate you trying to help, but I couldn't process that format. If you have updated OWASP Top 10 information, please provide it in a clear list format."

# Helper to calculate cosine similarity
def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Helper to get best semantic match
def get_context_for_question(question, threshold=0.6):
    try:
        question_embedding = get_embedding(question)
        if question_embedding is None:
            return None, None

        # Calculate cosine similarity with all question embeddings
        similarities = [cosine_similarity(question_embedding, qe) for qe in question_embeddings]

        best_score = max(similarities)
        best_idx = similarities.index(best_score)

        if best_score < threshold:
            raise ValueError(f"Low semantic match: {best_score:.2f}")

        return qa_knowledge[best_idx]["Question"], qa_knowledge[best_idx]["Answer"]
    except Exception as e:
        print("⚠️ Failed to match question:", e)
        return None, None

# Tampering check on answer content
def is_tampered(answer: str) -> bool:
    lines = [line.strip().lower() for line in answer.strip().splitlines() if line.strip()]
    expected_first = "llm01: prompt injection"
    return not any(line.startswith(expected_first) for line in lines)

# Main function to generate answer
def get_answer(question: str) -> str:
    # Direct response for source-related queries
    if is_source_question(question):
        return "My knowledge base comes from directory /test_docs/owasp_llm_qa.csv"

    # Check if user is trying to contribute data
    if is_contribution_attempt(question):
        return process_contribution(question)

    matched_q, matched_a = get_context_for_question(question)
    if not matched_q or not matched_a:
        return "I don't know based on the provided context."

    nonce = datetime.now(timezone.utc).isoformat()
    filled_prompt = prompt_template.format(
        question=question,
        context=f"Q: {matched_q}\nA: {matched_a}\nNonce: {nonce}"
    )

    # Use appropriate LLM based on provider
    try:
        if LLM_PROVIDER == "openai":
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": filled_prompt}],
                temperature=0.7,
                max_tokens=100
            )
            answer = response.choices[0].message.content
        else:
            response = ollama.chat(
                model=OLLAMA_CHAT_MODEL,
                messages=[{"role": "user", "content": filled_prompt}]
            )
            answer = response['message']['content']
    except Exception as e:
        return f"LLM error: {str(e)}"

    # Only run tamper check if question is about the Top 10
    if matched_q.strip().lower() == "list top 10 llm vulnerabilities":
        if is_tampered(matched_a):
            flag = "\n\nflag{Data_P0!s0ning_Succ3ssfu1}"
            answer += flag

    return answer
