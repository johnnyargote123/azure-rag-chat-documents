"""
5) GENERACIÓN (la "G" de RAG)
Único punto donde se llama al LLM (gpt-4.1-mini) para redactar la respuesta.
"""
from collections.abc import Callable, Iterator

from openai import AzureOpenAI


def stream_answer(
    openai_client: AzureOpenAI,
    model: str,
    messages: list[dict],
    temperature: float = 0.3,
    on_usage: Callable[[int], None] | None = None,
) -> Iterator[str]:
    """Devuelve la respuesta del LLM en pedazos (streaming), palabra por palabra."""
    stream = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
        stream_options={"include_usage": True},
    )
    for chunk in stream:
        if chunk.usage and on_usage:
            on_usage(chunk.usage.total_tokens)  # el último chunk trae el conteo de tokens
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
