import yaml
from langchain_core.vectorstores import VectorStoreRetriever
from src.vectorstore.chroma_client import ChromaClient
from utils.logger import get_logger
from utils.custom_exception import AppException

class AnimeRetriever:
    """
    Componente que gerencia a recuperação de documentos, configurado via YAML.
    """

    def __init__(self, chroma_client: ChromaClient, config_path: str = "config/retriever.yaml"):
        """
        Inicializa o retriever com o cliente do banco e as configurações externas.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.chroma_client = chroma_client
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> dict:
        """Carrega as configurações do YAML."""
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as exc:
            self.logger.error("Failed to load retriever.yaml")
            raise AppException("Configuration error", exc)

    def get_retriever(self) -> VectorStoreRetriever:
        """
        Configura e retorna o objeto retriever do LangChain baseado no YAML.
        """
        try:
            # 1. Identifica o tipo padrão definido no YAML (ex: similarity ou mmr)
            default_type = self.config.get("default_type", "similarity")
            # 2. Busca os parâmetros específicos para esse tipo
            settings = self.config["settings"][default_type]
            
            self.logger.info(
                "Configuring retriever | type=%s, params=%s", 
                default_type, settings["search_kwargs"]
            )
            
            # Carrega a instância ativa do banco de vetores
            vector_store = self.chroma_client.load_client()
            
            # 3. Instancia o retriever com os argumentos injetados do YAML
            return vector_store.as_retriever(
                search_type=settings["search_type"],
                search_kwargs=settings["search_kwargs"]
            )
            
        except Exception as exc:
            self.logger.error("Failed to configure dynamic LangChain retriever")
            raise AppException("Error during retriever setup", exc)