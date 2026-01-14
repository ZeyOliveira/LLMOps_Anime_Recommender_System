import logging
import os
from datetime import datetime
from typing import Optional

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: str,
    log_level: int = logging.INFO,
    log_dir: Optional[str] = "logs",
) -> logging.Logger:
    """
    Cria e retorna uma instância de logger configurada.

    Projetado para projetos de ML/MLOps, com suporte para

    registro em arquivo e no console sem duplicação de manipuladores.
    """

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False  # evita logs duplicados via root logger

    if logger.handlers:
        return logger  # evita múltiplos handlers

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Console handler (essencial para containers/cloud)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (opcional, mas comum em ML experiments)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(
            log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
