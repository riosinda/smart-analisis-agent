from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from app.core.config import settings

def get_llm():
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
        )
    
    elif settings.LLM_PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS,
            api_key=settings.GOOGLE_API_KEY,
        )
    
    elif settings.LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            temperature=settings.TEMPERATURE,
            base_url=settings.OLLAMA_BASE_URL,
        )
    
    else:
        raise ValueError(f"Proveedor no soportado: {settings.LLM_PROVIDER}")