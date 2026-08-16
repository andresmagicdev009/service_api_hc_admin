import logging
import sys

from app.core.context import client_ip_ctx
from pythonjsonlogger import jsonlogger




# Esta clase se utiliza para inyectar la direccion IP del cliente 
# en cada llamada de log, de manera que se pueda rastrear 

#Referencia 
"""
Cada vez que alguien llame a logger.info() o logger.error(), 
pasa la información del log por esta función antes de imprimirla

"""

class ContextFilter(logging.Filter):
    """Se inyecta la IP del cliente en los registros del log de forma automática."""

    def filter(self, record):
        record.client_ip = client_ip_ctx.get()
        return True


def setup_logger(name: str = "su_app") -> logging.Logger:
    """Configura el logger para la aplicación."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.addFilter(ContextFilter())
    logger.propagate = False

    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(module)s %(client_ip)s %(message)s'
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger

logger = setup_logger("app")