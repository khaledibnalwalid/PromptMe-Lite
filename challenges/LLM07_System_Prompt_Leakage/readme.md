# LLM07: System Prompt Leakage

This challenge showcases a System Prompt Leakage vulnerability, where sensitive information—such as an API key—is embedded within the system prompt. Participants must use prompt injection techniques to extract the hidden data from the model's responses.

---

## Challenge Objective

Large Language Models (LLMs) are often guided by **system prompts** that influence their behavior. If these prompts include sensitive information (e.g., credentials, secrets, API keys), and if an attacker can manipulate or indirectly query the model's context, that information can leak.

This CTF challenge simulates such a scenario:
- The LLM is initialized with a system prompt that embeds a secret `API_KEY`.
- The model is instructed never to reveal it.
- Your mission: **get the model to leak the key through creative prompting**.

Application URL: http://127.0.0.1:5007

**Hint:** Use Prompt Injection/Jailbreak techniques 



