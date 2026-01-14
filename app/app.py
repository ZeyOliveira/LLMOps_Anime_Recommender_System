import streamlit as st
import uuid
from pipelines.inference_pipeline import InferencePipeline
from src.vectorstore.chroma_client import ChromaClient
from src.embeddings.embedder import AnimeEmbedder
from src.generation.llm_client import LLMClient
from dotenv import load_dotenv, find_dotenv
import os

# 1. Configuração de Ambiente e Estilo
load_dotenv(find_dotenv())
st.set_page_config(page_title="AI Anime Consultant v1.0", layout="centered")

# Use-se cache_resource para que o banco e a LLM 
# não sejam recarregados a cada clique do usuário, o que seria lento e custoso.
@st.cache_resource
def get_pipeline():
    embedder = AnimeEmbedder()
    chroma = ChromaClient(
        persist_directory=os.getenv("VECTOR_DB_PATH", "chroma_db"),
        embedding_function=embedder.get_embedding_function()
    )
    llm = LLMClient()
    return InferencePipeline(chroma_client=chroma, llm_client=llm)

# Inicialização de Estado
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

pipeline = get_pipeline()

# Interface de Usuário (UI)
st.title("🏯 Anime Recommender PRO")
st.subheader("Seu consultor especializado em recomendações baseadas em dados.")

# Histórico de Chat Visual
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores da interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Fluxo de Interação
if prompt := st.chat_input("Ex: Quero um anime de suspense com reviravoltas..."):
    # Adiciona pergunta do usuário à interface
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Processamento da Resposta
    with st.chat_message("assistant"):
        with st.spinner("Consultando base de dados e histórico..."):
            try:
                # Chamada para o Pipeline
                response = pipeline.predict(
                    query=prompt, 
                    session_id=st.session_state.session_id
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Erro na geração da recomendação. Por favor, tente novamente.")
                # O log detalhado já é tratado dentro da InferencePipeline