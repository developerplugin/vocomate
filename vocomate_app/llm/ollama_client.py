import requests

def query_ollama(prompt, model="mistral", history=None, base_url="http://localhost:11434"):
    """
    Sends a prompt to a local Ollama LLM and returns the response.
    """
    url = f"{base_url}/api/chat"
    messages = history if history else []
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]

if __name__ == "__main__":
    reply = query_ollama("Hello! What can you do?")
    print("LLM Response:", reply)
