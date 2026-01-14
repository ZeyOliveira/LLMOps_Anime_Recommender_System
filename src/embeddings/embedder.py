import yaml
import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings 
from utils.logger import get_logger
from utils.custom_exception import AppException

class AnimeEmbedder:
    """
    Gerencia a geração de embeddings semânticos utilizando modelos configurados via YAML.
    """

    def __init__(self, config_path: str = "config/embeddings.yaml"):
        self.logger = get_logger(self.__class__.__name__)
        self.config = self._load_config(config_path)
        self.embedding_model = self._setup_embeddings()

    def _load_config(self, path: str) -> dict:
        """Carrega as configurações do YAML."""
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as exc:
            self.logger.error("Failed to load embeddings.yaml")
            raise AppException("Configuration error", exc)

    def _setup_embeddings(self):
        """
        Fábrica de Embeddings: Instancia o provedor baseado no default_provider do YAML.
        """
        provider_name = self.config.get("default_provider")
        conf = self.config["providers"][provider_name]
        
        self.logger.info("Initializing Embedding provider | provider=%s", provider_name)

        if provider_name == "huggingface":
            return HuggingFaceEmbeddings(
                model_name=conf["model_name"],
                model_kwargs={'device': conf.get("device", "cpu")},
                encode_kwargs=conf.get("encode_kwargs", {})
            )
        elif provider_name == "openai":
            return OpenAIEmbeddings(
                model=conf["model_name"],
                api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            raise AppException(f"Unsupported embedding provider: {provider_name}")

    def get_embedding_function(self):
        """Retorna a instância para uso no ChromaDB."""
        return self.embedding_model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Processamento em lote para indexação."""
        try:
            return self.embedding_model.embed_documents(texts)
        except Exception as exc:
            self.logger.error("Error during batch embedding generation")
            raise AppException("Failed to generate embeddings", exc)