from langchain_community.vectorstores import Chroma
from utils.logger import get_logger
from utils.custom_exception import AppException

class ChromaClient:
    """
    Interface especializada para operações no banco de vetores ChromaDB.
    """

    def __init__(self, persist_directory: str, embedding_function):
        """
        Inicializa o cliente do ChromaDB.

        Recebe a 'embedding_function' externamente (do AnimeEmbedder)
        para manter o desacoplamento, permitindo trocar o modelo sem alterar o banco.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function

    def create_from_documents(self, documents, collection_name: str = "anime_collection"):
        """
        Cria e persiste uma nova coleção a partir de documentos processados.

        Esta etapa é usada na 'indexing_pipeline.py' para 
        transformar os dados do loader em vetores permanentes no disco.
        """
        try:
            self.logger.info(
                "Creating vector store at %s | collection=%s", 
                self.persist_directory, collection_name
            )
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_function,
                persist_directory=self.persist_directory,
                collection_name=collection_name
            )
            self.logger.info("Vector store created and persisted successfully")
            return vector_store
        except Exception as exc:
            self.logger.error("Failed to create vector store from documents")
            raise AppException("Error during ChromaDB creation", exc)

    def load_client(self, collection_name: str = "anime_collection"):
        """
        Carrega uma instância existente do banco para consultas.

        Utilizado na 'inference_pipeline.py' para realizar buscas
        sem precisar reindexar os dados, economizando tempo e recursos.
        """
        try:
            self.logger.debug("Loading existing vector store from %s", self.persist_directory)
            return Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function,
                collection_name=collection_name
            )
        except Exception as exc:
            self.logger.error("Failed to load vector store")
            raise AppException("Error while connecting to ChromaDB", exc)