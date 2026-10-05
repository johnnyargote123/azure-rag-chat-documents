"""
6) ORQUESTACIÓN
Une los pasos en el orden del RAG:  Recuperar → Aumentar → Generar.
La interfaz solo habla con esta clase.
"""
from collections.abc import Callable, Iterator

from .clients import create_openai_client, create_search_client
from .config import Settings
from .generation import stream_answer
from .prompts import build_messages
from .retrieval import Source, search_documents


class RAGPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.search_client = create_search_client(settings)
        self.openai_client = create_openai_client(settings)

    def retrieve(self, question: str, top_k: int = 5) -> list[Source]:
        """Paso R: buscar fragmentos relevantes (sin LLM)."""
        return search_documents(self.search_client, question, top_k, self.settings.vector_field)

    def generate(
        self,
        question: str,
        sources: list[Source],
        history: list[dict],
        temperature: float = 0.3,
        on_usage: Callable[[int], None] | None = None,
    ) -> Iterator[str]:
        """Pasos A + G: armar el prompt y pedirle la respuesta al LLM."""
        messages = build_messages(question, sources, history)
        return stream_answer(
            self.openai_client, self.settings.chat_deployment, messages, temperature, on_usage
        )
