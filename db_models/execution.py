from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from db.db_connect import Base

class Execution(Base):
    __tablename__ = "executions"
    ID = Column(Integer, primary_key=True)
    Timestamp = Column(DateTime)
    Utm0 = Column(String)
    Utm1 = Column(String)
    Name = Column(String)
    Email = Column(String)
    Phone = Column(String)
    Webhook = Column(String)
    Etap = Column(String)
    Kontakt_z_doradca = Column(String)
    Deal_owner = Column(Integer)
    Termin_kursu_Amazon = Column(String)
    Zrodlo_Person = Column(Integer)
    Zrodlo_Deal = Column(Integer)
    Zrodlo_szczegolowe = Column(String)
    Wynik_testu = Column(String)
    Uwagi = Column(String)
    Url = Column(String)
    Kraj_rynek = Column(String)
    Input_json = Column(JSON)
    Error_message = Column(String)
    Execution_success = Column(Boolean)
    Output_json = Column(JSON)
    Person_id = Column(Integer)
    Person_owner_id = Column(Integer)

