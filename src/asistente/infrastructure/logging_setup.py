import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(root: Path) -> None:
    folder = root / "logs"
    folder.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(folder / "asistente.log", maxBytes=1_000_000,
                                  backupCount=3, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler()],
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)
