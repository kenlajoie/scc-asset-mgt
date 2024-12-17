from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:February14#@localhost:3306/todoapplicationdatabase'
#SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://ken:Cloud319#@192.168.123.23:3306/siam'
#engine = create_engine(SQLALCHEMY_DATABASE_URL)

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

