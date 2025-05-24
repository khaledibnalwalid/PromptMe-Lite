# Base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    libssl-dev \
    libffi-dev \
    ca-certificates

# Install Ollama (official binary)
RUN curl -fsSL https://ollama.com/install.sh | bash

# Pull the mistral model (during build or can be during container start)
RUN ollama pull mistral

# Set up the working directory
WORKDIR /app

# Copy your app code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the LLM service port
EXPOSE 5002

# Run the app and Ollama server
CMD ollama serve & python3 app2.py
