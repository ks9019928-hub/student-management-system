import os
from dotenv import load_dotenv

load_dotenv()


def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment (.env)."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def get_llm():
    """
    Initialize Gemini Chat Model via LangChain integration.
    Uses 'gemini-2.5-flash' for fast, accurate structured reasoning.
    """
    api_key = get_gemini_api_key()
    if not api_key or api_key == "your_gemini_api_key":
        return None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.0
        )
    except Exception as e:
        print(f"[Gemini LLM Init Warning]: {e}")
        return None
