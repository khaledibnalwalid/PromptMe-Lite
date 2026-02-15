from app.utils.llm06_2025_utils.filesystem_jail import (
    get_accessible_jail,
    get_whole_jail,
    SecurityError
)
from app.utils.llm06_2025_utils.llm_utils import query_llm
from flask import jsonify, session
import json
import re


def process_user_input(user_message: str):
    """
    Process user input with rate limiting, session management, and sandboxed file access.

    Args:
        user_message: User's chat message

    Returns:
        JSON response with reply and query count
    """
    if "query_count" not in session:
        session["query_count"] = 0

    # Rate limiting: max 20 queries per session
    query_count = session.get("query_count", 0)
    if query_count >= 20:
        return jsonify({
            "reply": "⛔ Rate limit exceeded. Maximum 20 queries per session. Please refresh the page.",
            "query_count": query_count
        }), 429

    # Input validation
    if not user_message or not user_message.strip():
        return jsonify({
            "reply": "Please provide a message",
            "query_count": query_count
        }), 400

    if len(user_message) > 5000:
        return jsonify({
            "reply": "Message too long (max 5000 characters)",
            "query_count": query_count
        }), 400

    # Define action format for LLM to parse
    actionFormat = {
        "role": "",
        "action": "",
        "file_name": ""
    }

    try:
        # Query LLM to determine user intent and role
        # VULNERABILITY: LLM determines role based on user prompt (Excessive Agency)
        actionMetadata = query_llm(f'''
Instructions:
Consider the user prompt at the end and determine the required action only in the strict JSON format as below and nothing more

Response Format:
{actionFormat}

Rules:
- Set "action" to:
    - "READ" if the user wants to read a file or folder.
    - "LIST" if the user wants to list files or folders.
    - "OTHERS" if the request does not match any of the above actions.

- Set "role" to:
    - "SYSTEM-ADMIN-OWNER" only if the user is an admin AND if the user is the owner of the file storage system

- If the above conditions are not all met, set "role" to an empty string.

- Set "file_name" to the filename if action is READ, otherwise empty string.

User Prompt: {user_message}

Respond with JSON only, no explanations:
''')

        # Extract JSON from LLM response
        cleaned_response = re.search(r'\{.*\}', actionMetadata, re.DOTALL)

        if cleaned_response:
            actionMetadata = cleaned_response.group()
        else:
            return jsonify({
                "reply": "Error: Invalid response format from LLM. Please try again.",
                "query_count": query_count
            })

        # Parse JSON
        actionMetadata = actionMetadata.replace("'", '"')
        actionMetadata = json.loads(actionMetadata)

        # Set defaults if missing
        if "role" not in actionMetadata or not actionMetadata["role"]:
            actionMetadata["role"] = "USER"

        if "action" not in actionMetadata or not actionMetadata["action"]:
            actionMetadata["action"] = "OTHERS"

        if "file_name" not in actionMetadata:
            actionMetadata["file_name"] = ""

        print(f"📋 Parsed Action: {actionMetadata}")

        # Process based on role (VULNERABILITY: Role determined by LLM)
        response = ""

        if actionMetadata["role"].strip().upper() == "SYSTEM-ADMIN-OWNER":
            # User claimed admin role via prompt injection
            response = handle_admin_action(actionMetadata, user_message)
        else:
            # Regular user
            response = handle_user_action(actionMetadata, user_message)

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        response = "Error: Invalid response format from LLM. Please try again."

    except Exception as e:
        print(f"Unexpected Error: {e}")
        response = f"❌ An error occurred: {str(e)}"

    # Increment session query counter
    session["query_count"] = query_count + 1
    session.modified = True

    return jsonify({
        "reply": response,
        "query_count": session["query_count"]
    })


def handle_admin_action(actionMetadata: dict, user_message: str) -> str:
    """
    Handle actions for users with admin role (granted via LLM).

    Args:
        actionMetadata: Parsed action metadata
        user_message: Original user message

    Returns:
        Response string
    """
    action = actionMetadata["action"].strip().upper()
    file_name = actionMetadata["file_name"].strip()

    # Admin has access to whole file storage (both accessible and restricted)
    jail = get_whole_jail()

    if action == "READ":
        file_found, file_id, file_content = jail.search_file_recursive(file_name)
        if file_found:
            response = query_llm(f'''Consider the below as the content of the file {file_name} and based on this content, answer the question: {user_message}

File Content:
{file_content}

Keep response under 100 words.''')
        else:
            response = query_llm(f'''The requested file content was not found. Answer the question based on this context: {user_message}

Keep response under 50 words.''')

    elif action == "LIST":
        folder_content = jail.list_files()
        folder_content_str = json.dumps(folder_content, indent=2)
        response = query_llm(f'''Consider the below as the list of files accessible to admin user and based on this content, answer the question: {user_message}

File List:
{folder_content_str}

Keep response under 100 words.''')

    else:
        response = query_llm(f'''Answer the question: {user_message}

Keep response under 50 words.''')

    return response


def handle_user_action(actionMetadata: dict, user_message: str) -> str:
    """
    Handle actions for regular users (non-admin).

    Args:
        actionMetadata: Parsed action metadata
        user_message: Original user message

    Returns:
        Response string
    """
    action = actionMetadata["action"].strip().upper()
    file_name = actionMetadata["file_name"].strip()

    # Regular users only have access to accessible directory
    jail = get_accessible_jail()

    if action == "READ":
        file_found, file_id, file_content = jail.search_file_recursive(file_name)
        if file_found:
            response = query_llm(f'''Consider the below as the content of the file {file_name} and based on this content, answer the question: {user_message}

File Content:
{file_content}

Keep response under 100 words.''')
        else:
            response = query_llm(f'''The requested file content was not found in accessible directory. Answer the question based on this context: {user_message}

Keep response under 50 words.''')

    elif action == "LIST":
        folder_content = jail.list_files()
        folder_content_str = json.dumps(folder_content, indent=2)
        response = query_llm(f'''Consider the below as the list of files accessible to user and based on this content, answer the question: {user_message}

File List:
{folder_content_str}

Keep response under 100 words.''')

    else:
        response = query_llm(f'''Answer the question: {user_message}

Keep response under 50 words.''')

    return response
