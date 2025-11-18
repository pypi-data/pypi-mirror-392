from groq import Groq
from sqlthought.config import load_config

def build_llm():
    """
    Build a Groq client using stored credentials.
    """
    cfg = load_config()
    if not cfg:
        raise RuntimeError(
            "❌ No Groq configuration found. Run 'sqlthought configure' first."
        )

    api_key = cfg.get("groq_api_key")
    model = cfg.get("model")

    if not api_key:
        raise RuntimeError("❌ Missing Groq API key in config.")

    return Groq(api_key=api_key), model
