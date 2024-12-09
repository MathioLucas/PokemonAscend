from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = "sqlite:///./pokemon_dashboard.db"  

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass= StaticPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()