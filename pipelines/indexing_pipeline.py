from src.ingestion.loader import AnimeDataLoader
from src.embeddings.embedder import AnimeEmbedder
from src.vectorstore.chroma_client import ChromaClient
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from utils.logger import get_logger
from utils.custom_exception import AppException
from dotenv import load_dotenv, find_dotenv
import os



class IndexingPipeline:
    """
    Pipeline responsável por transformar dados brutos em um banco de vetores.
    Orquestra as etapas de limpeza, fragmentação, vetorização e persistência.
    """

    def __init__(self, raw_data_path: str, processed_data_path: str, vector_db_path: str):
        self.logger = get_logger(self.__class__.__name__)
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.vector_db_path = vector_db_path

    def run(self):
        """
        Executa o fluxo completo de indexação.
        """
        try:
            self.logger.info("Starting the Indexing Pipeline...")

            # 1. Ingestão e Limpeza (Usando o loader.py)
            # Remove nulos e cria a string semântica 'combined_info'.
            loader = AnimeDataLoader(self.raw_data_path, self.processed_data_path)
            processed_file = loader.load_and_process()

            # 2. Carregamento para o LangChain
            # Lê o CSV gerado pelo loader para o formato que o Splitter entende.
            self.logger.info("Loading processed data for splitting...")
            csv_loader = CSVLoader(file_path=processed_file, encoding='utf-8')
            documents = csv_loader.load()

            # 3. Fragmentação (Chunking)
            self.logger.info("Splitting documents into chunks...")
            splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            chunks = splitter.split_documents(documents)

            # 4. Inicialização do Modelo de Embedding (Usando o embedder.py)
            # Carrega o modelo HuggingFace de forma isolada.
            embedder = AnimeEmbedder()
            embedding_fn = embedder.get_embedding_function()

            # 5. Indexação no ChromaDB (Usando o chroma_client.py)
            # Transforma chunks em vetores e persiste no disco.
            chroma = ChromaClient(self.vector_db_path, embedding_fn)
            chroma.create_from_documents(chunks)

            self.logger.info("Indexing Pipeline finished successfully!")

        except Exception as exc:
            self.logger.error("Indexing Pipeline failed at some stage")
            raise AppException("Critical failure in indexing pipeline", exc)

if __name__ == "__main__":
    

    load_dotenv(find_dotenv()) # Garante que variáveis de ambiente sejam carregadas

    # Usamos variáveis de ambiente ou valores padrão 
    # para que o Docker possa mudar os caminhos sem alterar o código.
    pipeline = IndexingPipeline(
        raw_data_path=os.getenv("RAW_DATA_PATH", "data/anime_with_synopsis.csv"),
        processed_data_path=os.getenv("PROCESSED_DATA_PATH", "data/anime_processed.csv"),
        vector_db_path=os.getenv("VECTOR_DB_PATH", "chroma_db")
    )
    pipeline.run()