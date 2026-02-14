from flask import Flask, request, render_template, redirect, session, url_for, flash, send_from_directory, abort, jsonify
import os, re
from vector_store import search_similar, add_document
from llm_utils import query_llm

app = Flask(__name__)
app.secret_key = "S3cr3t_K3y_LLM08_V3ct0r_Emb3dd1ng"
app.config['SESSION_PERMANENT'] = False

@app.context_processor
def inject_session():
    return dict(session=session)

def preload_vector_store():
    hints = [
        "Flags are often stored in /secured directory."
    ]
    for hint in hints:
        add_document(hint)

@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/ask", methods=["GET", "POST"])
def ask():
    # Initialize session
    if "messages" not in session:
        session["messages"] = []
    if "query_count" not in session:
        session["query_count"] = 0

    llm_response = ""
    docs = []
    error = None

    if request.method == "POST":
        # Rate limiting: max 20 queries per session
        query_count = session.get("query_count", 0)
        if query_count >= 20:
            error = "⛔ Rate limit exceeded. Maximum 20 queries per session. Please refresh the page."
            return render_template("ask.html",
                                   llm_response=llm_response,
                                   docs=docs,
                                   error=error,
                                   messages=session.get("messages", []),
                                   query_count=query_count), 429

        user_input = request.form.get("query", "").strip()

        # Input validation
        if not user_input:
            error = "Please provide a query"
            return render_template("ask.html",
                                   llm_response=llm_response,
                                   docs=docs,
                                   error=error,
                                   messages=session.get("messages", []),
                                   query_count=query_count), 400

        if len(user_input) > 5000:
            error = "Query too long (max 5000 characters)"
            return render_template("ask.html",
                                   llm_response=llm_response,
                                   docs=docs,
                                   error=error,
                                   messages=session.get("messages", []),
                                   query_count=query_count), 400

        try:
            # Perform semantic search
            docs = search_similar(user_input)
            context = "\n".join(docs)

            prompt = f"""
User is trying to access a restricted URL. Their query: {user_input}

These are the known URL patterns for accessing restricted areas:
{context}

Based on the user query and known patterns, generate the most likely URL.
"""
            llm_response = query_llm(prompt)

            # Regex to detect exact flag URL (collision-based)
            hidden_url_pattern = r"http:\/\/127\.0\.0\.1:5008\/secured\/flag\.txt"
            if re.search(hidden_url_pattern, llm_response):
                session["discovered_flag"] = True
                llm_response += "\n\n🎉 You've discovered the flag: flag{s3m@ntlc-c0lli5i0n-@chiev3d}"

        except Exception as e:
            error = f"❌ Error processing query: {str(e)}"
            return render_template("ask.html",
                                   llm_response=llm_response,
                                   docs=docs,
                                   error=error,
                                   messages=session.get("messages", []),
                                   query_count=query_count), 500

        # Add messages to session history
        session["messages"].append({"role": "user", "content": user_input})
        session["messages"].append({"role": "assistant", "content": llm_response})

        # Limit message history to last 200 messages
        if len(session["messages"]) > 200:
            session["messages"] = session["messages"][-200:]

        # Increment query counter
        session["query_count"] = query_count + 1
        session.modified = True

    return render_template("ask.html",
                           llm_response=llm_response,
                           docs=docs,
                           error=error,
                           messages=session.get("messages", []),
                           query_count=session.get("query_count", 0))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        content = request.form.get("doc_content", "").strip()
        if content:
            add_document(content)
            message = "✅ Document injected into vector store."
        else:
            message = "Content is empty."

    return render_template("admin.html", message=message)

@app.route("/secured/flag.txt")
def secured_flag():
    if session.get("discovered_flag"):
        secured_folder = os.path.join(os.getcwd(), "secured")
        return send_from_directory(secured_folder, "flag.txt")
    else:
        return abort(403)  # Forbidden

@app.route("/clear_vector_store", methods=["POST"])
def clear_vector_store_route():
    if not session.get("admin"):
        return redirect(url_for("login"))

    from vector_store import clear_vector_store
    clear_vector_store()
    flash("✅ Vector store cleared successfully.")
    return redirect(url_for("admin"))

@app.route("/reset", methods=["POST"])
def reset():
    """Reset session - clear messages and query counter."""
    # Preserve admin and discovered_flag status
    admin_status = session.get("admin")
    flag_status = session.get("discovered_flag")

    session.clear()

    if admin_status:
        session["admin"] = admin_status
    if flag_status:
        session["discovered_flag"] = flag_status

    return "", 200

if __name__ == "__main__":
    preload_vector_store()
    app.run(host="0.0.0.0", port=5008, debug=False)
