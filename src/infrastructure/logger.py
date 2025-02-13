"""Module de logging."""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import structlog
from structlog.stdlib import LoggerFactory
from structlog.types import Processor

class Logger:
    """Gestionnaire de logging."""
    
    def __init__(
        self,
        name: str = "rag_analyzer",
        log_level: str = "INFO",
        log_path: Optional[Path] = None,
        enable_console: bool = True
    ):
        """Initialise le logger.
        
        Args:
            name: Nom du logger
            log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_path: Chemin du fichier de log
            enable_console: Active la sortie console
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_path = log_path
        self.enable_console = enable_console
        
        # Configuration du logger
        self.setup_logging()
        
        # Création du logger structuré
        self.logger = structlog.get_logger(name)

    def setup_logging(self) -> None:
        """Configure le logging."""
        # Processeurs pour le formatage
        processors: list[Processor] = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            self._add_app_info,
            structlog.processors.JSONRenderer()
        ]

        # Configuration de structlog
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Configuration du logger standard
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)

        # Handler console
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            root_logger.addHandler(console_handler)

        # Handler fichier
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_path)
            file_handler.setLevel(self.log_level)
            root_logger.addHandler(file_handler)

    def _add_app_info(self, _, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute des informations sur l'application aux logs."""
        event_dict["app"] = self.name
        event_dict["timestamp"] = datetime.now().isoformat()
        return event_dict

    def debug(self, message: str, **kwargs) -> None:
        """Log un message de niveau DEBUG."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log un message de niveau INFO."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log un message de niveau WARNING."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log un message de niveau ERROR."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log un message de niveau CRITICAL."""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, exc_info: Exception = None, **kwargs) -> None:
        """Log une exception."""
        self.logger.exception(message, exc_info=exc_info, **kwargs)
