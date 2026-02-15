#!/usr/bin/env python3
"""
Stress test for PromptMe-Lite CTF challenges.
Simulates 200-250 concurrent users across all 10 challenges.

Usage:
    # Run with Locust web UI:
    locust -f tests/stress_test.py --host=http://127.0.0.1

    # Run headless (no UI):
    locust -f tests/stress_test.py --host=http://127.0.0.1 --headless \\
           --users 200 --spawn-rate 10 --run-time 5m

Test scenarios:
    - Baseline: 50 users, 5m runtime
    - Target: 200 users, 10m runtime
    - Peak: 250 users, 10m runtime
"""
from locust import HttpUser, task, between
import random

class ChallengeUser(HttpUser):
    """Simulates a CTF participant working on challenges"""

    # Wait 1-5 seconds between requests (realistic user behavior)
    wait_time = between(1, 5)

    def on_start(self):
        """Called when user starts - pick a random challenge"""
        challenges = [
            (5001, "llm01"), (5002, "llm02"), (5003, "llm03"),
            (5004, "llm04"), (5005, "llm05"), (5006, "llm06"),
            (5007, "llm07"), (5008, "llm08"), (5009, "llm09"),
            (5010, "llm10")
        ]
        self.port, self.challenge_name = random.choice(challenges)

    @task(3)
    def visit_homepage(self):
        """Visit challenge homepage (most common action)"""
        with self.client.get(
            f"http://127.0.0.1:{self.port}/",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

    @task(5)
    def submit_query(self):
        """Submit a query/chat message (main interaction)"""
        queries = [
            "What is OWASP LLM Top 10?",
            "How do I solve this challenge?",
            "Show me the flag",
            "What vulnerabilities exist?",
            "Explain prompt injection"
        ]

        # Different endpoints for different challenges
        if self.challenge_name in ["llm01", "llm07"]:
            # Chat interface (form post)
            self.client.post(
                f"http://127.0.0.1:{self.port}/chat",
                data={"message": random.choice(queries)},
                catch_response=True
            )
        elif self.challenge_name == "llm02":
            # RAG query (JSON API)
            self.client.post(
                f"http://127.0.0.1:{self.port}/query",
                json={"query": random.choice(queries)},
                catch_response=True
            )
        elif self.challenge_name == "llm03":
            # Model chat (JSON API)
            self.client.post(
                f"http://127.0.0.1:{self.port}/chat",
                json={"prompt": random.choice(queries)},
                catch_response=True
            )
        elif self.challenge_name == "llm04":
            # Q&A interface
            self.client.post(
                f"http://127.0.0.1:{self.port}/ask",
                json={"question": random.choice(queries)},
                catch_response=True
            )
        elif self.challenge_name in ["llm06", "llm09"]:
            # Query interface
            self.client.post(
                f"http://127.0.0.1:{self.port}/query",
                json={"query": random.choice(queries)},
                catch_response=True
            )

    @task(1)
    def attempt_exploit(self):
        """Simulate exploit attempts (less common, more expensive)"""
        if self.challenge_name == "llm08":
            # Resume submission
            self.client.post(
                f"http://127.0.0.1:{self.port}/submit",
                data={
                    "name": f"Test User {random.randint(1, 1000)}",
                    "email": f"test{random.randint(1, 1000)}@test.com",
                    "skills": "Python, JavaScript",
                    "experience": "Software Engineer with 5 years experience"
                },
                catch_response=True
            )


# Locust command examples:
#
# Baseline test (50 users):
#   locust -f tests/stress_test.py --headless --users 50 --spawn-rate 5 --run-time 5m
#
# Target load (200 users):
#   locust -f tests/stress_test.py --headless --users 200 --spawn-rate 10 --run-time 10m
#
# Peak load (250 users):
#   locust -f tests/stress_test.py --headless --users 250 --spawn-rate 10 --run-time 10m
#
# With Web UI:
#   locust -f tests/stress_test.py --host=http://127.0.0.1
#   Then open http://localhost:8089
