import logging
from commands.subte.suscribers.models import SubteSuscription, Session
from utils.decorators import log_time

logger = logging.getLogger(__name__)


@log_time
def add_subte_suscriber(user_id, name, linea):
    session = Session()
    suscription = SubteSuscription(user_id=user_id, user_name=name, linea=linea)
    session.add(suscription)
    session.commit()


def remove_subte_suscriber(user_id, line):
    session = Session()
    suscription = session.query(SubteSuscription).filter_by(user_id=user_id, linea=line).first()
    if suscription is None:
        logger.info("Suscription (%s, %s) does not exist on db", user_id, line)
        deleted = False
    else:
        session.delete(suscription)
        session.commit()
        logger.info("Suscription (%s, %s) DELETED", user_id, line)
        deleted = True

    return deleted


@log_time
def get_suscriptors():
    session = Session()
    return session.query(SubteSuscription).all()


@log_time
def get_suscriptors_by_line(line):
    session = Session()
    return session.query(SubteSuscription).filter_by(linea=line).all()
