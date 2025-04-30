from sqlalchemy import Column, String, Integer, ForeignKey, DateTime    # type: ignore
from sqlalchemy.orm import relationship                                 # type: ignore
from database import Base
import pytz
from datetime import datetime

class Brand(Base):
    __tablename__ = "brand"
    
    name = Column(String, primary_key=True)
    normalized_name = Column(String, nullable=True)
    language = Column(String, nullable=False)

class Operator(Base):
    __tablename__ = "operator"
    
    code = Column(String, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

class Admin(Base):
    __tablename__ = "admin"
    
    code = Column(String, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

class Log(Base):
    __tablename__ = "log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operator_code = Column(String, ForeignKey("operator.code"), nullable=False) # Codice dell'operatore
    brand_name = Column(String, ForeignKey("brand.name"), nullable=False)       # Nome del brand
    cart = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(pytz.timezone("Europe/Rome")))
    
    operator = relationship("Operator", foreign_keys=[operator_code])           # Relazione: log_record.operator restituisce la tupla dell'operatore
    brand = relationship("Brand", foreign_keys=[brand_name])                    # Relazione: log_record.brand restituisce la tupla del brand