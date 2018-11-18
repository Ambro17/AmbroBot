import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)


class Meeting(Base):
    __tablename__ = 'meeting'

    id = Column(Integer, primary_key=True)

    name = Column(String)
    datetime = Column(TIMESTAMP(timezone=True))
    expired = Column(Boolean, default=False)

    def __repr__(self):
        return "<Meeting(name='%s', datetime='%s', expired=%s)>" % (
            self.name,
            self.datetime,
            self.expired,
        )
