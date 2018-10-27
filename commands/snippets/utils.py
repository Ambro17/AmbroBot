import logging
import os
import psycopg2

from decorators import log_time

logger = logging.getLogger(__name__)
DB = os.environ['DATABASE_URL']


@log_time
def save_to_db(key, content):
    try:
        with psycopg2.connect(DB) as conn:
            with conn.cursor() as curs:
                curs.execute("INSERT INTO bot_memory (key, content) VALUES (%s, %s);", (key, content))
                logger.info(f"Content successfully added to db with key '{key}'")
                conn.commit()
                success = True
    except Exception:
        logger.exception("Error writing to db")
        success = False

    return success


@log_time
def lookup_content(key):
    try:
        with psycopg2.connect(DB) as conn:
            with conn.cursor() as curs:
                curs.execute('SELECT key, content from bot_memory WHERE key=%s;', (key,))
                content = curs.fetchone()
                logger.info("Content retrieved under key %s", key)
                conn.commit()
                return content

    except Exception:
        logger.exception("Error writing to db")
        return None


@log_time
def select_all():
    try:
        with psycopg2.connect(DB) as conn:
            with conn.cursor() as curs:
                curs.execute('SELECT * FROM bot_memory')
                content = curs.fetchall()
                conn.commit()
                return content

    except Exception:
        logger.exception("Error writing to db")
        return None


@log_time
def remove_snippet(key):
    try:
        with psycopg2.connect(DB) as conn:
            with conn.cursor() as curs:
                curs.execute('DELETE FROM bot_memory WHERE key=%s', (key,))
                conn.commit()
                logger.info("Status: %s", curs.statusmessage)
                return curs.statusmessage == 'DELETE 1'
    except Exception:
        logger.exception("Error writing to db")
        return False
