# PromptMe-Lite Usage Guide

## Quick Start

### Option 1: Start All Challenges at Once (Recommended for Testing/Events)

```bash
# Using the convenience script
./start_all.sh

# Or using Python directly
python3 main.py --start-all
```

This will:
- ✅ Check for `.env` configuration file
- ✅ Verify Python dependencies are installed
- ✅ Start all 10 challenges on ports 5001-5010
- ✅ Launch the dashboard on port 5000
- ✅ Create log files in `./logs/` directory

### Option 2: Production Mode (No Dashboard)

```bash
# Start all challenges without the dashboard
python3 main.py --no-dashboard

# Or using the script
./start_all.sh --no-dashboard
```

Use this for production deployments where you only need the challenges running.

### Option 3: Dashboard Only (Original Behavior)

```bash
python3 main.py
```

Then click "Start Challenge" buttons in the dashboard to launch challenges on-demand.

---

## Command-Line Options

```bash
python3 main.py [OPTIONS]

Options:
  --start-all       Start all 10 challenges before launching dashboard
  --no-dashboard    Start all challenges without dashboard (production mode)
  --help           Show this help message
```

---

## Startup Modes Comparison

| Mode | Command | Challenges | Dashboard | Use Case |
|------|---------|-----------|-----------|----------|
| **Dashboard Only** | `python3 main.py` | On-demand | ✅ Yes | Development, selective testing |
| **Start All + Dashboard** | `python3 main.py --start-all` | All 10 auto-start | ✅ Yes | CTF events, full testing |
| **Production Mode** | `python3 main.py --no-dashboard` | All 10 auto-start | ❌ No | Production deployment, stress tests |

---

## Challenge Ports

| Challenge | Port | Vulnerability |
|-----------|------|---------------|
| LLM01 | 5001 | Prompt Injection |
| LLM02 | 5002 | Sensitive Info Disclosure |
| LLM03 | 5003 | Supply Chain |
| LLM04 | 5004 | Data & Model Poisoning |
| LLM05 | 5005 | Improper Output Handling |
| LLM06 | 5006 | Excessive Agency |
| LLM07 | 5007 | System Prompt Leakage |
| LLM08 | 5008 | Vector & Embedding Weaknesses |
| LLM09 | 5009 | Misinformation |
| LLM10 | 5010 | Unbounded Consumption |

**Dashboard:** Port 5000 (if enabled)

---

## Logs

All challenge logs are stored in `./logs/` directory:

```bash
logs/
├── challenge_5001.log  # LLM01
├── challenge_5002.log  # LLM02
├── ...
└── challenge_5010.log  # LLM10
```

To monitor logs in real-time:

```bash
# Watch all logs
tail -f logs/*.log

# Watch specific challenge
tail -f logs/challenge_5001.log
```

---

## Stopping Challenges

### Stop All Challenges

```bash
# If running in foreground
Ctrl+C

# If running in background (with --no-dashboard)
pkill -f "python3 main.py"

# Or kill specific ports
kill $(lsof -t -i:5001)  # Stop LLM01
```

### Stop from Dashboard

Navigate to `http://127.0.0.1:5000` and use the "Stop All" button or individual "Stop" buttons.

---

## Validation & Testing

### Validate All Challenges Are Running

```bash
python3 tests/validate_flags.py
```

This checks if all 10 challenges are responsive on their ports.

### Stress Test (200-250 Concurrent Users)

```bash
# Install locust first
pip3 install locust

# Run stress test with 200 users
locust -f tests/stress_test.py --headless \
       --users 200 --spawn-rate 10 --run-time 10m

# Monitor resources during test
./tests/monitor.sh
```

### Production Deployment with Gunicorn

```bash
# Start with gunicorn for better performance
gunicorn -c gunicorn_config.py main:app
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :5001

# Kill the process
kill $(lsof -t -i:5001)
```

### Dependencies Not Installed

```bash
pip3 install -r requirements.txt
```

### Missing .env File

```bash
cp .env.example .env
# Then edit .env with your configuration
```

### Check Challenge Status

```bash
# List all processes on challenge ports
for port in {5001..5010}; do
    echo "Port $port: $(lsof -i :$port | grep LISTEN || echo 'NOT RUNNING')"
done
```

---

## Examples

### Full CTF Event Setup

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env to set LLM_PROVIDER (ollama or openai)

# 3. Start all challenges + dashboard
./start_all.sh

# 4. Validate all challenges are working
python3 tests/validate_flags.py

# 5. Run stress test to verify capacity
locust -f tests/stress_test.py --headless --users 200 --spawn-rate 10 --run-time 5m
```

### Production Deployment

```bash
# 1. Set production environment variables
export LLM_PROVIDER=ollama
export FLASK_ENV=production

# 2. Start all challenges without dashboard
python3 main.py --no-dashboard &

# 3. Monitor in background
./tests/monitor.sh
```

### Development Workflow

```bash
# 1. Start just the dashboard
python3 main.py

# 2. Open browser to http://127.0.0.1:5000

# 3. Click individual "Start Challenge" buttons as needed

# 4. Test specific challenges

# 5. Stop individual challenges from dashboard
```

---

## Performance Notes

- **Ollama (Local)**: No rate limits, supports 250+ concurrent users
- **OpenAI**: Requires Tier 2+ ($50+ spend) for 200+ users
- **Memory**: ~3-4GB total for all 10 challenges
- **CPU**: Recommend 4+ cores for 200+ concurrent users
- **Response Times**:
  - Homepage: < 500ms
  - LLM queries: 2-5 seconds (varies by provider and model)

---

## Configuration

### LLM Provider Selection

Edit `.env` file:

```bash
# Use local Ollama (recommended for 200+ users)
LLM_PROVIDER=ollama
OLLAMA_CHAT_MODEL=granite3.1-moe:1b

# OR use OpenAI (requires API key and Tier 2+ for scale)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

### Session Configuration

Sessions automatically reset on page refresh. Configure timeout in individual challenge files if needed:

```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
```

---

For more information, see:
- [README.md](README.md) - Project overview
- [tests/stress_test.py](tests/stress_test.py) - Load testing details
- [gunicorn_config.py](gunicorn_config.py) - Production deployment config
