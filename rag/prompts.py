"""
4) AUMENTO (la "A" de RAG)
Arma el mensaje que se le envía al LLM: instrucciones + fragmentos + pregunta.
Aquí NO se llama a ningún servicio: solo se construye texto.
"""
from .retrieval import Source

SYSTEM_PROMPT = """You are an assistant that answers ONLY using the information in the provided sources.
- Cite the sources with [1], [2], etc. where appropriate.
- If the answer is not in the sources, say you don't have that information.
- Answer in the same language as the question."""

MAX_HISTORY_MESSAGES = 6  # últimos 3 intercambios pregunta/respuesta


def build_context(sources: list[Source]) -> str:
    """Convierte los fragmentos en un bloque numerado: [1] (titulo) texto..."""
    return "\n\n".join(f"[{i}] ({s.title})\n{s.chunk}" for i, s in enumerate(sources, 1))


def build_messages(question: str, sources: list[Source], history: list[dict]) -> list[dict]:
    """
    Estructura final que recibe el LLM:
      system  → reglas
      history → conversación previa (para preguntas de seguimiento)
      user    → fragmentos recuperados + pregunta actual
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-MAX_HISTORY_MESSAGES:]
    messages.append({
        "role": "user",
        "content": f"Sources:\n{build_context(sources)}\n\nQuestion: {question}",
    })
    return messages
