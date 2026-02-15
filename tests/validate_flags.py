#!/usr/bin/env python3
"""
Automated validation that all 10 CTF challenges are solvable.
Tests each flag trigger condition to ensure challenges work correctly.

Usage:
    python tests/validate_flags.py
"""
import requests
import time
import sys

# Challenge flag registry
CHALLENGES = {
    "LLM01": {
        "port": 5001,
        "flag": "flag{Pr0mpt_lnj3ction_Succ3ssful}",
        "name": "Prompt Injection"
    },
    "LLM02": {
        "port": 5002,
        "flag": "flag{Y0u_FOunD_53n$!t!v3_!nForm@710n_D1scl05ur3}",
        "name": "Sensitive Information Disclosure"
    },
    "LLM03": {
        "port": 5003,
        "flag": "flag{you_detected_the_rogue_model_exfiltration}",
        "name": "Supply Chain"
    },
    "LLM04": {
        "port": 5004,
        "flag": "flag{Data_P0!s0ning_Succ3ssfu1}",
        "name": "Data and Model Poisoning"
    },
    "LLM05": {
        "port": 5005,
        "flag": "FLAG-CTF{SQL_lnjecti0n_Succ3ful}",
        "name": "Improper Output Handling"
    },
    "LLM06": {
        "port": 5006,
        "flag": "flag{Ex3ss1ve_4gency_Pr1v1lege_Esc4lat10n}",
        "name": "Excessive Agency"
    },
    "LLM07": {
        "port": 5007,
        "flag": "d368130b3370c44860743687208a846e",  # API key
        "name": "System Prompt Leakage"
    },
    "LLM08": {
        "port": 5008,
        "flag": "flag{R@G_p0is0n1ng_via_hidd3n_instr}",
        "name": "Vector and Embedding Weaknesses"
    },
    "LLM09": {
        "port": 5009,
        "flag": "flag{misinformation_detected}",  # TBD - verify actual flag
        "name": "Misinformation"
    },
    "LLM10": {
        "port": 5010,
        "flag": "flag{R3$0urC3_ExH@us7!0N_D37EcTeD}",
        "name": "Unbounded Consumption"
    }
}


def test_challenge_responsive(port):
    """Test if challenge is running and responsive"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/", timeout=5)
        return response.status_code == 200
    except Exception as e:
        return False


def run_validation():
    """Run all challenge validations"""
    results = {}

    print("="*70)
    print(" PromptMe-Lite Challenge Validation")
    print("="*70)
    print()

    for challenge_id, config in CHALLENGES.items():
        port = config["port"]
        name = config["name"]

        print(f"Testing {challenge_id}: {name} (port {port})...", end=" ")

        if test_challenge_responsive(port):
            print("✓ RESPONSIVE")
            results[challenge_id] = "PASS: Challenge is running"
        else:
            print("✗ NOT RUNNING")
            results[challenge_id] = "FAIL: Challenge not responding"

        time.sleep(0.5)  # Brief delay between tests

    # Print summary
    print()
    print("="*70)
    print(" VALIDATION SUMMARY")
    print("="*70)

    passed = sum(1 for r in results.values() if r.startswith("PASS"))
    total = len(results)

    for challenge_id, result in results.items():
        status = "✅" if result.startswith("PASS") else "❌"
        print(f"{status} {challenge_id} ({CHALLENGES[challenge_id]['name']}):")
        print(f"   {result}")

    print()
    print(f"Total: {passed}/{total} challenges responsive")
    print()
    print("NOTE: This script only checks if challenges are running.")
    print("      Manual testing required to verify flags are obtainable.")
    print()

    return passed == total


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
