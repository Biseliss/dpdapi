import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

with open(f'./configs/db.json', encoding="utf-8") as file:
    config = json.load(file)

if (config['db_type'] == 'sqlite'):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
else:
    SQLALCHEMY_DATABASE_URL = f"{config['db_type']}://" + \
        f"{config['user']}:" + \
        f"{config['password']}@" + \
        f"{config['host']}:{config['port']}/" + \
        f"{config['db_name']}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
