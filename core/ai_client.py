import google.generativeai as genai
import ollama

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7


def list_gemini_models(api_key: str) -> list[str]:
    """List available models for the given API key."""
    if not api_key:
        return [DEFAULT_MODEL, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    genai.configure(api_key=api_key)
    try:
        models = genai.list_models()
        return [m.name.replace("models/", "") for m in models if 'generateContent' in m.supported_generation_methods]
    except Exception:
        return [DEFAULT_MODEL, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]



def call_gemini(prompt: str, api_key: str, config: dict) -> str:
    """Send prompt to Gemini and return the text response."""
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Add it to your .env file.")

    genai.configure(api_key=api_key)
    model_name = config.get("model", DEFAULT_MODEL)
    temperature = float(config.get("temperature", DEFAULT_TEMPERATURE))

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=genai.types.GenerationConfig(temperature=temperature),
    )
    response = model.generate_content(prompt)
    return response.text


def list_ollama_models() -> list[str]:
    """List available models from the local Ollama instance."""
    try:
        response = ollama.list()
        if hasattr(response, 'models'):
            return [m.model for m in response.models]
        else:
            return [m.get('model', m.get('name')) for m in response.get('models', [])]
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return []


def call_ollama(prompt: str, config: dict) -> str:
    """Send prompt to local Ollama instance."""
    model_name = config.get("model", "llama3.2")
    temperature = float(config.get("temperature", DEFAULT_TEMPERATURE))
    
    response = ollama.generate(model=model_name, prompt=prompt, options={"temperature": temperature})
    return response['response']
