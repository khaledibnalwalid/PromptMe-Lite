import os
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def generate_with_openai(model_name, history, prompt):
    """Generate response using OpenAI native client (following app1.py pattern)"""
    try:
        messages = history + [{"role": "user", "content": prompt}]
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
