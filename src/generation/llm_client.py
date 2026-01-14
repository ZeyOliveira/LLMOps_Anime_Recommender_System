import yaml
import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from src.prompts.templates import get_anime_prompt
from utils.logger import get_logger
from utils.custom_exception import AppException
from operator import itemgetter


class LLMClient:
    """
    Orquestrador de Geração que gerencia provedores de LLM e executa a 
    cadeia de raciocínio (RAG Chain) usando LCEL.
    """

    def __init__(self, config_path: str = "config/llm.yaml"):
        self.logger = get_logger(self.__class__.__name__)
        self.config = self._load_config(config_path)
        self.llm = self._setup_llm()

    def _load_config(self, path: str) -> dict:
        """Carrega as configurações do YAML."""
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as exc:
            self.logger.error("Failed to load llm.yaml")
            raise AppException("Configuration error", exc)

    def _setup_llm(self):
        """
        Fábrica de Modelos: Instancia o provedor baseado no default_provider do YAML.
        
        Centraliza a criação do objeto LLM, permitindo trocar de 
        Groq para OpenAI sem alterar os pipelines de inferência.
        """
        provider_name = self.config.get("default_provider")
        conf = self.config["providers"][provider_name]
        
        self.logger.info("Initializing LLM provider | provider=%s", provider_name)

        if provider_name == "groq":
            return ChatGroq(
                model_name=conf["model"]["name"],
                temperature=conf["model"]["temperature"],
                max_tokens=conf["model"]["max_tokens"],
                api_key=os.getenv("GROQ_API_KEY")
            )
        elif provider_name == "openai":
            return ChatOpenAI(
                model_name=conf["model"]["name"],
                temperature=conf["model"]["temperature"],
                max_tokens=conf["model"]["max_tokens"],
                api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            raise AppException(f"Unsupported provider: {provider_name}")
        

    def get_chain(self, retriever):
        """
        Constrói a cadeia RAG usando LangChain Expression Language (LCEL).
        
        - RunnablePassthrough: Garante que a pergunta do usuário passe direto para o prompt.
        - format_docs: Função auxiliar interna para limpar os documentos vindo do retriever.
        """
        prompt = get_anime_prompt()
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.logger.debug("Assembling LCEL RAG chain with dictionary handling")

        # Usa-se itemgetter("question") para extrair apenas o texto antes de enviar ao retriever
        chain = (
            {
                "context": itemgetter("question") | retriever | format_docs, 
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history")
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain