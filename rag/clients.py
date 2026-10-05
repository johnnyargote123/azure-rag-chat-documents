"""
2) CONEXIONES
Crea los clientes para hablar con Azure. Solo construye los objetos;
no busca ni genera nada todavía.
"""
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

from .config import Settings


def create_search_client(settings: Settings) -> SearchClient:
    """Cliente para Azure AI Search (donde están los documentos indexados)."""
    return SearchClient(
        endpoint=settings.search_endpoint,
        index_name=settings.search_index,
        credential=AzureKeyCredential(settings.search_api_key),
    )


def create_openai_client(settings: Settings) -> AzureOpenAI:
    """Cliente para Azure OpenAI (el LLM que redacta las respuestas)."""
    return AzureOpenAI(
        api_key=settings.openai_api_key,
        azure_endpoint=settings.openai_endpoint,
        api_version=settings.openai_api_version,
    )
