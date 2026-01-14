from typing import Dict
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.vectorstore.chroma_client import ChromaClient
from src.retrieval.retriever import AnimeRetriever
from src.generation.llm_client import LLMClient
from utils.logger import get_logger
from utils.custom_exception import AppException

class InferencePipeline:
    """
    Orquestrador de Inferência (RAG + Memória).
    Unifica a busca no ChromaDB com a geração da LLM, mantendo o histórico
    de conversas isolado por sessão na RAM.
    """

    def __init__(self, chroma_client: ChromaClient, llm_client: LLMClient):
        """
        Inicializa a pipeline com injeção de dependências.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.llm_client = llm_client
        
        # AnimeRetriever busca as configurações no retriever.yaml automaticamente.
        self.retriever = AnimeRetriever(chroma_client).get_retriever()
        
        # 2. Obtém a base da Chain (esteira de processamento)
        self.base_chain = self.llm_client.get_chain(self.retriever)
        
        # 3. Gerenciador de Memória Local (Dicionário na RAM)
        self.session_store: Dict[str, InMemoryChatMessageHistory] = {}
        
        # 4. Cria a Chain Final com suporte a histórico
        self.runnable_chain = self._setup_history_chain()

    def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Recupera ou cria um histórico para uma sessão específica."""
        if session_id not in self.session_store:
            self.logger.info("Creating new chat session | session_id=%s", session_id)
            self.session_store[session_id] = InMemoryChatMessageHistory()
        return self.session_store[session_id]

    def _setup_history_chain(self):
        """
        Envolve a chain base com lógica de histórico de mensagens.
        
        O 'RunnableWithMessageHistory' é o padrão atual do LangChain 
        para gerenciar automaticamente a entrada/saída de memória na chain.
        """
        return RunnableWithMessageHistory(
            self.base_chain,
            get_session_history=self._get_session_history,
            input_messages_key="question",
            history_messages_key="chat_history",
        )

    def predict(self, query: str, session_id: str = "default_user") -> str:
        """
        Executa a inferência completa para uma pergunta do usuário.
        
        Args:
            query: A pergunta ou preferência de anime do usuário.
            session_id: Identificador único da conversa (essencial para produção).
        """
        try:
            self.logger.info("Processing query | session=%s", session_id)
            
            # Executa a esteira (Chain) com o ID da sessão
            response = self.runnable_chain.invoke(
                {"question": query},
                config={"configurable": {"session_id": session_id}}
            )
            
            return response
            
        except Exception as exc:
            self.logger.error("Inference failed for session %s", session_id)
            raise AppException("Critical error during recommendation generation", exc)