import pandas as pd
from typing import Set

from utils.logger import get_logger
from utils.custom_exception import AppException


class AnimeDataLoader:
    """
    Responsável pela ingestão e pré-processamento semântico do conjunto de dados de anime.

    Este componente transforma dados estruturados brutos
    em uma representação textual consolidada, adequada para incorporações (embeddings)
    e indexação RAG subsequente.
    """

    REQUIRED_COLUMNS: Set[str] = {"Name", "Genres", "sypnopsis"}

    def __init__(self, original_csv: str, processed_csv: str):
        self.original_csv = original_csv
        self.processed_csv = processed_csv
        self.logger = get_logger(self.__class__.__name__)

    def load_and_process(self) -> str:
        """
        Carrega o conjunto de dados CSV bruto, valida o esquema, cria um campo de texto semântico unificado e persiste o artefato processado.

        Retorna:

        str: Caminho para o arquivo CSV processado contendo `combined_info`.

        Exceções:

        AppException: Se alguma etapa de ingestão ou processamento falhar.
        """
        try:
            self.logger.info("Starting data ingestion")
            df = self._load_csv()
            self._validate_schema(df)
            df = self._build_combined_info(df)
            self._persist(df)

            self.logger.info(
                "Data ingestion completed successfully | output=%s",
                self.processed_csv,
            )
            return self.processed_csv

        except Exception as exc:
            self.logger.error(
                "Failed during data ingestion pipeline",
                exc_info=True,
            )
            raise AppException(
                message="Error while loading and processing anime dataset",
                original_exception=exc,
            )

    def _load_csv(self) -> pd.DataFrame:
        self.logger.debug("Loading raw CSV file: %s", self.original_csv)
        return (
            pd.read_csv(
                self.original_csv,
                encoding="utf-8",
                on_bad_lines="skip",
            )
            .dropna()
            .reset_index(drop=True)
        )

    def _validate_schema(self, df: pd.DataFrame) -> None:
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"Missing required columns in dataset: {missing}"
            )
        self.logger.debug("Dataset schema validation passed")

    def _build_combined_info(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.debug("Building combined semantic text field")

        df["combined_info"] = (
            "Title: "
            + df["Name"]
            + " | Overview: "
            + df["sypnopsis"]
            + " | Genres: "
            + df["Genres"]
        )

        return df[["combined_info"]]

    def _persist(self, df: pd.DataFrame) -> None:
        self.logger.debug(
            "Persisting processed dataset to %s", self.processed_csv
        )
        df.to_csv(self.processed_csv, index=False, encoding="utf-8")
