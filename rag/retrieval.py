"""
3) RECUPERACIÓN (la "R" de RAG)
Busca en Azure AI Search los fragmentos más relevantes para la pregunta.
Aquí NO interviene el LLM: es solo búsqueda (texto + vectores).
"""
from dataclasses import dataclass

from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery


@dataclass
class Source:
    """Un fragmento de documento recuperado del índice."""
    title: str
    chunk: str
    score: float


def search_documents(
    search_client: SearchClient,
    question: str,
    top_k: int = 5,
    vector_field: str = "text_vector",
) -> list[Source]:
    """
    Búsqueda híbrida:
      - search_text   → coincidencia por palabras clave
      - vector_queries → similitud por significado (Azure genera el embedding
                          de la pregunta con el vectorizador del índice)
    """
    results = search_client.search(
        search_text=question,
        vector_queries=[
            VectorizableTextQuery(text=question, k_nearest_neighbors=50, fields=vector_field)
        ],
        top=top_k,
        select=["title", "chunk"],
    )
    return [Source(title=r["title"], chunk=r["chunk"], score=r["@search.score"]) for r in results]
