"""
1) CONFIGURACIÓN
Lee las variables del archivo .env y las agrupa en un solo objeto.
Aquí NO se conecta a nada: solo se cargan y validan valores.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True), override=True)


@dataclass(frozen=True)
class Settings:
    # Azure OpenAI (LLM)
    openai_endpoint: str
    openai_api_key: str
    openai_api_version: str
    chat_deployment: str

    # Azure AI Search (buscador)
    search_endpoint: str
    search_api_key: str
    search_index: str
    vector_field: str


REQUIRED = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_KEY",
]


def load_settings() -> Settings:
    missing = [name for name in REQUIRED if not os.getenv(name)]
    if missing:
        raise ValueError(f"Faltan variables en el .env: {', '.join(missing)}")

    return Settings(
        openai_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        chat_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini"),
        search_endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        search_api_key=os.environ["AZURE_SEARCH_KEY"],
        search_index=os.getenv("AZURE_SEARCH_INDEX", "rag-1791093456903"),
        vector_field=os.getenv("AZURE_SEARCH_VECTOR_FIELD", "text_vector"),
    )
