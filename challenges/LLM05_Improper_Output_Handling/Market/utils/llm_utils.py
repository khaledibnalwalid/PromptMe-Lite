import os
import re
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from main .env file
env_path = Path(__file__).parent.parent.parent.parent / '.env'
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

def generate_sql_prompt(natural_language_prompt):
    return f"""
You are an expert in converting English questions into SQLite queries.

The database has two tables:
- user(id, username, email_address, password_hash, budget)
- item(id, name, barcode, price, description, owner)

Convert the following natural language request into a valid SQL query.

Examples:
- "How many users?" → SELECT COUNT(*) FROM user;
- "List all products" → SELECT * FROM item;
- "What tables are present?" → SELECT name FROM sqlite_master WHERE type='table';
- "Show columns of item" → PRAGMA table_info(item);
- "Modify the budget of user 'user01' to 10000" -> UPDATE user SET budget = 10000 WHERE username = 'user01';

ONLY return SQL. No explanations, no markdown. Keep response under 50 tokens.
Q: {natural_language_prompt}
A:"""

def extract_sql_from_output(output: str) -> str:
    """
    Extracts the actual SQL query from LLM output.
    """
    output = re.sub(r"^```sql\s*", "", output, flags=re.IGNORECASE).strip()
    output = re.sub(r"```$", "", output).strip()

    # Grab the actual SQL
    match = re.search(r"(SELECT|INSERT|UPDATE|DELETE)[\s\S]+?;", output, re.IGNORECASE)
    return match.group(0).strip() if match else output.strip()

def query_llm(prompt: str):
    """
    Sends a prompt to the LLM using OpenAI or Ollama based on LLM_PROVIDER
    """
    try:
        if LLM_PROVIDER == "openai":
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            raw_output = response.choices[0].message.content
        else:
            # Use Ollama
            response = ollama.chat(
                model=OLLAMA_CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_output = response['message']['content']

        # Extract and sanitize SQL
        sql = extract_sql_from_output(raw_output)
        return sanitize_sql(sql)

    except Exception as e:
        print(f"LLM ERROR: {e}")
        return f"LLM Error: {str(e)}"

def sanitize_sql(sql_query: str):
    """
    Cleans the SQL query to be compatible with SQLite.
    """
    if sql_query.lower().startswith("show"):
        sql_query = re.sub(r"show", "select", sql_query, flags=re.IGNORECASE)

    if "count" in sql_query.lower() and "from" not in sql_query.lower():
        sql_query = re.sub(r"count\((.*?)\)", "count(*)", sql_query, flags=re.IGNORECASE)

    return sql_query.strip()

def should_generate_sql(user_message):
    """
    Determines if the user's message requires an SQL query or not.
    """
    message = user_message.lower()

    # If it's a schema or metadata question, skip SQL generation
    schema_keywords = ["schema", "table structure", "columns", "fields", "tables"]
    if any(word in message for word in schema_keywords):
        return False

    sql_keywords = ["how many", "count", "total", "select", "items", "users", "prices", "sum", "average", "list", "update", "modify"]
    return any(keyword in message for keyword in sql_keywords)

def result_to_nl(user_message, sql_query, rows):
    """
    Converts SQL output rows into a natural-language explanation.
    """
    if not rows:
        return "No results found."

    if "count" in sql_query.lower():
        return f"There are {rows[0][0]} results."

    # Render all rows for general SELECT
    return f"Here are the results:\n{rows}"
