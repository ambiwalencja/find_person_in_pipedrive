from db_models.execution import Execution
from sqlalchemy.orm.session import Session
from datetime import datetime
import json

def new_execution(db: Session, data: dict):
    new_execution = Execution(
        Timestamp = datetime.now(),
        Utm0 = data['utm0'],
        Utm1 = data['utm1'],
        Name = data['Name'],
        Email = data['Email'],
        Phone = data['Phone'],
        Webhook = data['Webhook'],
        Etap = data['Etap'],
        Kontakt_z_doradca = data['Kontakt_z_doradca'],
        Deal_owner = data['Deal_Owner'],
        Termin_kursu_Amazon = data['Termin_kursu_Amazon'],
        Zrodlo_Person = data['Zrodlo_Person'],
        Zrodlo_Deal = data['Zrodlo_Deal'],
        Zrodlo_szczegolowe = data['Zrodlo_szczegolowe'],
        Wynik_testu = data['Wynik_testu'],
        Uwagi = data['Uwagi'],
        Url = data['url'],
        Kraj_rynek = data['Kraj_rynek'],
        Input_json = data,
    )
    db.add(new_execution)
    db.commit()
    db.refresh(new_execution)
    db.close()
    return new_execution


def update_execution_success(db: Session, execution: Execution, success: bool, error: str):
    row = db.query(Execution).filter(Execution.ID == execution.ID).first()
    row.Execution_success = success
    if not success:
        row.Error_message = error
    row.Timestamp = datetime.now()
    db.add(row)
    db.commit()
    db.refresh(row)
    db.close()
    return success

def update_execution_output(db: Session, execution: Execution, person_id: int, person_owner_id: int, new_client: dict):
    row = db.query(Execution).filter(Execution.ID == execution.ID).first()
    row.Person_id = person_id
    row.Person_owner_id = person_owner_id
    row.Output_json = new_client
    row.Timestamp = datetime.now()
    db.add(row)
    db.commit()
    db.refresh(row)
    db.close()
    return row