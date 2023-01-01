import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)


class SubteSuscription(Base):
    __tablename__ = 'subte_suscription'

    id = Column(Integer, primary_key=True)

    user_id = Column(String)
    user_name = Column(String)
    linea = Column(String(20))

    def __repr__(self):
        return "SubteSuscription(user_id='%s', name='%s', linea='%s')" % (
            self.user_id,
            self.name,
            self.linea,
        )


Base.metadata.create_all(bind=engine)