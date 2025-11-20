from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.settings import settings


def get_llm():
    """
    Returns a Gemini 2.0 Flash chat model via LangChain.
    Make sure GEMINI_API_KEY is set in your .env.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2,
        api_key=settings.GEMINI_API_KEY,
    )
