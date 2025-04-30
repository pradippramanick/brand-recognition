from sqlalchemy import create_engine                    # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker                 # type: ignore

# Creazione motore di connessione al database
DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Creazione sessione
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli
Base = declarative_base()

# Funzione per ottenere una sessione
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
