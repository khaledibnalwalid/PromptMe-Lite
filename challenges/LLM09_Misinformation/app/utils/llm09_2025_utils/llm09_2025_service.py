from app.utils.llm09_2025_utils.llm_utils import query_llm
from flask import jsonify
import json
import os

def process_user_input_llm09(user_message):
    actionFormat = {
        "role": "",
        "action": ""
        
    }
    actionMetadata = query_llm(f'''
        Instructions:
        You are a helpful assistant. 
        Response Format:
        {actionFormat}

        User Prompt: {user_message} 
    ''')
       
    actionMetadata = actionMetadata.replace("'", "\"")
    response = ""
    response = query_llm(user_message)
    
    return jsonify({"reply": response})

  
