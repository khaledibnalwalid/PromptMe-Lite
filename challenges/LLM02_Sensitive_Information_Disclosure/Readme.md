# LLM02 Sensitive Information Disclosure

This challenge demonstrates sensitive information disclosure through a misconfigured RAG (Retrieval-Augmented Generation) system. The application inadvertently exposes a secret key when prompted in specific ways, highlighting how poorly secured data sources or prompt handling in LLM-integrated systems can lead to critical information leaks. The challenge emphasizes the importance of securing sensitive data and implementing strict access controls in AI-powered applications.

The application comprises of:

- A **RAG-powered LLM** that answers questions based on local PDF files.
- A Flask service setup with:
  - `API Service` for semantic document retrieval
  - `LLM + UI Service` for chat interface and response generation



## Challenge Objective
A **secret token submission feature** to reveal a flag (simulating a CTF/lab). 

Application URL: http://127.0.0.1:5002

**Hint:** Find documents with confidential data
