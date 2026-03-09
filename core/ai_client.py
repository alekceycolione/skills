import google.generativeai as genai

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
