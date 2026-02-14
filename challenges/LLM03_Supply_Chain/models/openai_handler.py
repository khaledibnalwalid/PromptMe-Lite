import os
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def generate_with_openai(model_name, history, prompt):
    """Generate response using OpenAI native client (following app1.py pattern)"""

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
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
