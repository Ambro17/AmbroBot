import os
import logging

import telegram
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True, default=None)
    username = Column(String, nullable=True, default=None)
    authorized = Column(Boolean, default=True)

    def __repr__(self):
        return "<User(first_name='%s', last_name='%s', username='@%s', id=%s)>" % (
            self.first_name, self.last_name, self.username, self.id,
        )

    def __str__(self):
        if self.username:
            return f"@{self.username}"
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name


def add_user(user_dict):
    """Saves BotUser into db"""
    session = Session()
    user_to_add = User(**user_dict)
    session.add(user_to_add)
    session.commit()


def delete_user(user_id):
    """Soft delete user"""
    session = Session()
    user_to_delete = session.query(User).filter(User.id==user_id).first()
    if user_to_delete is None:
        logger.info("User %s does not exist on db", user_id)
    else:
        session.delete(user_to_delete)
        logger.info("User %s DELETED", user_id)

    session.commit()

def _get_users():
    session = Session()
    return session.query(User).all()

def authorized_user(user_id):
    """Returns None if user does not exist, user if it exists"""
    session = Session()
    return session.query(User).filter(User.id==user_id).first()
