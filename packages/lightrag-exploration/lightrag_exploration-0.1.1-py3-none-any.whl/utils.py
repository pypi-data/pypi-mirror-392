import httpx

def get_ollama_host():
    return "http://localhost:11434"
    
def get_ollama_models():
    """Fetch available models from Ollama API."""
    url = f"{get_ollama_host()}/api/tags"
    with httpx.Client(
        timeout=httpx.Timeout(10.0, read=30.0)
    ) as client:
        response = client.get(url)
    response.raise_for_status()
    return response.json().get("models", [])

def get_ollama_summary(text: str, model: str = "gemma3:1b"):
    """Get a summary of the text using Ollama API."""
    url = f"{get_ollama_host()}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes text.",
            },
            {
                "role": "system",
                "content": "Please return the output in formatted html.",
            },
            {
                "role": "system",
                "content": "Use HTML tags like <p>, <b>, <i>, <ul>, <li> for formatting.",
            },
            {"role": "system", "content": "Use nice css styles to make it look cool."},
            {
                "role": "system",
                "content": "Only respond with the HTML content, no explanations.",
            },
            {"role": "user", "content": text},
        ],
    }
    with httpx.Client(
        timeout=httpx.Timeout(10.0, read=120.0)
    ) as client:
        response = client.post(url, json=payload)
    response.raise_for_status()
    generated_text = response.json()["choices"][0]["message"]["content"]

    # Remove markdown code block markers if present
    if generated_text.startswith("```html"):
        generated_text = generated_text[len("```html") :].strip()
    if generated_text.endswith("```"):
        generated_text = generated_text[:-3].strip()
    return generated_text