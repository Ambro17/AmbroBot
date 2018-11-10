import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)


class RetroItem(Base):
    __tablename__ = 'retro_items'

    id = Column(Integer, primary_key=True)

    user = Column(String)
    text = Column(String)
    datetime = Column(TIMESTAMP(timezone=True))
    expired = Column(Boolean, default=False)

    def __repr__(self):
        return "<Item(user='%s', text='%s', datetime='%s', expired=%s)>" % (
            self.user, self.text, self.datetime, self.expired
        )
