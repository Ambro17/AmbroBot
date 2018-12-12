import logging
from commands.subte.suscribers.db import add_subte_suscriber

logger = logging.getLogger(__name__)


def add_suscriber_to_linea(user_id, name, linea):
    try:
        add_subte_suscriber(user_id, name, linea)
        return True
    except Exception:
        logger.info("Error saving subte suscriber", exc_info=True)
        return False
