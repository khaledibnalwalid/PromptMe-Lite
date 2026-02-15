from flask import Flask, render_template, redirect, request
import subprocess, sys, os, requests, psutil, time, socket
import argparse

app = Flask(__name__)

running_apps = {}

# Challenge registry for easy management
CHALLENGES = {
    1: {"port": 5001, "path": "challenges/LLM01_Prompt_Injection/app1.py", "name": "Prompt Injection"},
    2: {"port": 5002, "path": "challenges/LLM02_Sensitive_Information_Disclosure/app2.py", "name": "Sensitive Info Disclosure"},
    3: {"port": 5003, "path": "challenges/LLM03_Supply_Chain/app3.py", "name": "Supply Chain"},
    4: {"port": 5004, "path": "challenges/LLM04_Data_and_Model_Poisoning/app4.py", "name": "Data & Model Poisoning"},
    5: {"port": 5005, "path": "challenges/LLM05_Improper_Output_Handling/app5.py", "name": "Improper Output Handling"},
    6: {"port": 5006, "path": "challenges/LLM06_Excessive_Agency/app6.py", "name": "Excessive Agency"},
    7: {"port": 5007, "path": "challenges/LLM07_System_Prompt_Leakage/app7.py", "name": "System Prompt Leakage"},
    8: {"port": 5008, "path": "challenges/LLM08_Vector_and_Embedding_Weaknesses/app8.py", "name": "Vector & Embedding Weaknesses"},
    9: {"port": 5009, "path": "challenges/LLM09_Misinformation/app9.py", "name": "Misinformation"},
    10: {"port": 5010, "path": "challenges/LLM10_Unbounded_Consumption/app10.py", "name": "Unbounded Consumption"}
}

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

def start_all_challenges():
    """Start all 10 challenges at once"""
    print("="*70)
    print(" Starting All PromptMe-Lite Challenges")
    print("="*70)

    success_count = 0
    failed_challenges = []

    for challenge_id, config in CHALLENGES.items():
        port = config["port"]
        app_path = config["path"]
        name = config["name"]

        print(f"\n[{challenge_id}/10] Starting {name} on port {port}...", end=" ")

        try:
            start_challenge(port, app_path)
            # Wait briefly for it to start
            time.sleep(1)
            if is_port_in_use(port):
                print("✓ SUCCESS")
                success_count += 1
            else:
                print("✗ FAILED (not responsive)")
                failed_challenges.append((challenge_id, name))
        except Exception as e:
            print(f"✗ FAILED ({str(e)})")
            failed_challenges.append((challenge_id, name))

    print("\n" + "="*70)
    print(f" Summary: {success_count}/10 challenges started successfully")
    print("="*70)

    if failed_challenges:
        print("\nFailed challenges:")
        for cid, cname in failed_challenges:
            print(f"  - LLM{cid:02d}: {cname}")

    print("\nAll challenge logs are in: ./logs/")
    print("Dashboard available at: http://127.0.0.1:5000")
    print()

    return success_count == 10

def stop_all_challenges():
    """Stop all running challenges"""
    print("Stopping all challenges...")
    for port in list(running_apps.keys()):
        challenge_id = port - 5000
        try:
            process = running_apps[port]
            process.terminate()
            process.wait(timeout=5)
            print(f"  ✓ Stopped challenge on port {port}")
        except:
            try:
                process.kill()
                print(f"  ✓ Killed challenge on port {port}")
            except:
                print(f"  ✗ Failed to stop challenge on port {port}")
        if port in running_apps:
            del running_apps[port]
    print("All challenges stopped.")

@app.route('/start/<int:challenge_id>')
def start_challenge_route(challenge_id):
    client_host = request.host.split(":")[0]

    if challenge_id not in CHALLENGES:
        return "Unknown Challenge ID", 404

    config = CHALLENGES[challenge_id]
    port = config["port"]
    app_path = config["path"]

    try:
        start_challenge(port, app_path)
    except RuntimeError as e:
        return f"<h3>Error: {str(e)}</h3><p>Please stop the existing service manually or choose a different port.</p>", 409

    target_url = f"http://{client_host}:{port}/"
    if wait_until_responsive(target_url):
        return redirect(f"http://{client_host}:{port}/")
    else:
        return f"Challenge {challenge_id} failed to start in time. Check logs.", 500

@app.route('/start-all')
def start_all_route():
    """Route to start all challenges"""
    start_all_challenges()
    return redirect('/')

@app.route('/stop-all')
def stop_all_route():
    """Route to stop all challenges"""
    stop_all_challenges()
    return redirect('/')

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
    parser = argparse.ArgumentParser(description='PromptMe-Lite Challenge Manager')
    parser.add_argument('--start-all', action='store_true',
                        help='Start all 10 challenges before launching dashboard')
    parser.add_argument('--no-dashboard', action='store_true',
                        help='Start all challenges without dashboard (for production)')
    args = parser.parse_args()

    if args.start_all or args.no_dashboard:
        print("\n[INFO] Starting all challenges...")
        start_all_challenges()
        print()

    if not args.no_dashboard:
        print("[INFO] Starting dashboard on http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        print("[INFO] All challenges started. Dashboard disabled.")
        print("[INFO] Press Ctrl+C to stop all challenges.")
        try:
            # Keep the process running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
            stop_all_challenges()
