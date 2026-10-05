"""
7) INTERFAZ (Streamlit)
Solo se encarga de mostrar cosas en pantalla y recibir preguntas.
Toda la lógica del RAG está en la carpeta rag/.

Ejecutar:  python -m streamlit run app.py
"""
import streamlit as st

from rag import RAGPipeline, Source, load_settings

st.set_page_config(page_title="Chat con mis documentos", page_icon="💬")


# ---------- Inicialización (una sola vez) ----------
@st.cache_resource
def get_pipeline() -> RAGPipeline:
    return RAGPipeline(load_settings())


try:
    pipeline = get_pipeline()
except ValueError as e:
    st.error(str(e))
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "tokens" not in st.session_state:
    st.session_state.tokens = 0


# ---------- Componentes visuales ----------
def show_sources(sources: list[Source]) -> None:
    with st.expander(f"📚 Fuentes ({len(sources)})"):
        for i, s in enumerate(sources, 1):
            st.markdown(f"**[{i}] {s.title}** · score {s.score:.3f}")
            st.caption(s.chunk[:400] + ("…" if len(s.chunk) > 400 else ""))


# ---------- Barra lateral ----------
with st.sidebar:
    st.header("⚙️ Configuración")
    top_k = st.slider("Fragmentos a recuperar", 1, 10, 5)
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.3, 0.1)
    if st.button("🗑️ Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tokens = 0
        st.rerun()
    st.divider()
    tokens_placeholder = st.empty()  # se actualiza al terminar cada respuesta


def render_tokens() -> None:
    tokens_placeholder.caption(f"Tokens usados en esta sesión: {st.session_state.tokens:,}")


render_tokens()


# ---------- Encabezado ----------
st.title("💬 Chat con mis documentos")
st.caption(
    f"Azure AI Search (`{pipeline.settings.search_index}`) + `{pipeline.settings.chat_deployment}`"
)

# ---------- Historial ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            show_sources(msg["sources"])

# ---------- Nueva pregunta ----------
if question := st.chat_input("Pregunta algo sobre tus documentos…"):
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        # Paso R — búsqueda en Azure AI Search (sin LLM)
        with st.spinner("🔎 Buscando en tus documentos…"):
            sources = pipeline.retrieve(question, top_k)

        # Pasos A + G — prompt + respuesta del LLM
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

        def add_tokens(n: int) -> None:
            st.session_state.tokens += n

        answer = st.write_stream(
            pipeline.generate(question, sources, history, temperature, on_usage=add_tokens)
        )
        show_sources(sources)

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    render_tokens()
