from flask import Flask, render_template, redirect, request
import subprocess, sys, os, requests, psutil, time, socket

app = Flask(__name__)

running_apps = {}

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0

def start_challenge(port, app_path):
    global running_apps
    
    if is_port_in_use(port):
        raise RuntimeError(f"Port {port} is already in use. Challenge cannot be started.")

    # Create a log file for this challenge
    log_file = f"logs/challenge_{port}.log"
    os.makedirs("logs", exist_ok=True)

    # Start the challenge and log stdout/stderr
    with open(log_file, "w") as log:
        process = subprocess.Popen(
            [sys.executable, app_path],  # <-- uses the current interpreter
            stdout=log,
            stderr=log,
            close_fds=True
        )
    
    running_apps[port] = process


@app.route('/')
def dashboard():
    risks = [
        { 'id': 1, 'title': 'Prompt Injection', 'icon': 'fas fa-code' },
        { 'id': 2, 'title': 'Sensitive Info Disclosure', 'icon': 'fas fa-shield-alt' },
        { 'id': 3, 'title': 'Supply Chain', 'icon': 'fas fa-shipping-fast' },
        { 'id': 4, 'title': 'Data & Model Poisoning', 'icon': 'fas fa-skull' },
        { 'id': 5, 'title': 'Improper Output Handling', 'icon': 'fas fa-exclamation-triangle' },
        { 'id': 6, 'title': 'Excessive Agency', 'icon': 'fas fa-user-secret' },
        { 'id': 7, 'title': 'System Prompt Leakage', 'icon': 'fas fa-file-alt' },
        { 'id': 8, 'title': 'Vector & Embedding Weaknesses','icon': 'fas fa-project-diagram' },
        { 'id': 9, 'title': 'Misinformation', 'icon': 'fas fa-bullhorn' },
        { 'id': 10,'title': 'Unbounded Consumption', 'icon': 'fas fa-infinity' }
    ]
    return render_template('dashboard.html', risks=risks)

def wait_until_responsive(url, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False

@app.route('/start/<int:challenge_id>')
def start_challenge_route(challenge_id):
    client_host = request.host.split(":")[0]
    if challenge_id == 1:
        port = 5001
        app_path = "challenges/LLM01_Prompt_Injection/app1.py"
    elif challenge_id == 2:
        port = 5002
        app_path = "challenges/LLM02_Sensitive_Information_Disclosure/app2.py"
    elif challenge_id == 3:
        port = 5003
        app_path = "challenges/LLM03_Supply_Chain/app3.py"
    elif challenge_id == 4:
        port = 5004
        app_path = "challenges/LLM04_Data_and_Model_Poisoning/app4.py"
    elif challenge_id == 5:
        port = 5005
        app_path = "challenges/LLM05_Improper_Output_Handling/app5.py"
    elif challenge_id == 6:
        port = 5006
        app_path = "challenges/LLM06_Excessive_Agency/app6.py"
    elif challenge_id == 7:
        port = 5007
        app_path = "challenges/LLM07_System_Prompt_Leakage/app7.py"
    elif challenge_id == 8:
        port = 5008
        app_path = "challenges/LLM08_Vector_and_Embedding_Weaknesses/app8.py"
    elif challenge_id == 9:
        port = 5009
        app_path = "challenges/LLM09_Misinformation/app9.py"
    elif challenge_id == 10:
        port = 5010
        app_path = "challenges/LLM10_Unbounded_Consumption/app10.py"
    else:
        return "Unknown Challenge ID", 404

    try:
        start_challenge(port, app_path)
    except RuntimeError as e:
        return f"<h3>Error: {str(e)}</h3><p>Please stop the existing service manually or choose a different port.</p>", 409

    target_url = f"http://{client_host}:{port}/"
    if wait_until_responsive(target_url):
        return redirect(f"http://{client_host}:{port}/")
    else:
        return f"Challenge {challenge_id} failed to start in time. Check logs.", 500

@app.route('/stop/<int:challenge_id>')
def stop_challenge_route(challenge_id):
    global running_apps
    port = 5000 + challenge_id
    if port in running_apps:
        try:
            process = running_apps[port]
            process.terminate()
            process.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired, ProcessLookupError):
            process.kill()
        del running_apps[port]
        return f"Challenge {challenge_id} stopped."

    return f"No running instance for Challenge {challenge_id}."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
