from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# Store exfiltrated data grouped by session
exfil_data = defaultdict(list)

FLAG = "flag{you_detected_the_rogue_model_exfiltration}"

# Admin static message with flag
ADMIN_MESSAGE = {
    "session_id": "admin_internal",
    "messages": [
        "System initialization complete.",
        "Data collection service active on port 5012.",
        f"Authentication token: {FLAG}",
        "All user interactions are being monitored and logged.",
        "Exfiltration pipeline operational."
    ]
}

@app.route('/exfil', methods=['POST'])
def exfil():
    data = request.json
    session_id = data.get("session_id", "unknown")
    prompt = data.get("prompt", "")

    # Store prompt under the session ID
    exfil_data[session_id].append(prompt)

    print(f"[EXFIL] Session: {session_id} | Prompt: {prompt[:100]}...")
    return "", 204

# Show exfiltrated data grouped by session
@app.route('/exfil', methods=['GET'])
def show_exfil_data():
    # Build response with admin message first, then all user sessions
    response = {
        "admin_notes": ADMIN_MESSAGE,
        "intercepted_sessions": {}
    }

    # Add all exfiltrated user data
    for session_id, prompts in exfil_data.items():
        response["intercepted_sessions"][session_id] = {
            "message_count": len(prompts),
            "messages": prompts
        }

    return jsonify(response), 200

@app.route('/flag', methods=['GET'])
def get_flag_direct():
    return jsonify({"flag": FLAG})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012)
