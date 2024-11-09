from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy import cast, Date

from rq import Queue
from rq.job import Job
from db.redis_connection import get_redis_connection
from db.db_connect import get_db

from schemas.find_person_schemas import FindPersonInPipedrive
from find_person_utils.find_person import find_person_in_pipedrive

from typing import Optional, List
from db.db_find_person import new_execution
from db_models.execution import Execution

from auth.oauth2 import get_current_user
from schemas.users_schemas import UserAuth


router = APIRouter(
    prefix="/find_person_in_pipedrive",
    tags=["find_person_in_pipedrive"],
    responses={404: {"description": "Not found"}},
)

@router.post("/run_directly") # without redis
def run_find_person_in_pipedrive(request: FindPersonInPipedrive, dry: bool=True):
    new_client_json_output = find_person_in_pipedrive(request.model_dump(), dry)
    return new_client_json_output

@router.post("/run") # with redis
def run_find_person_in_queue(request: FindPersonInPipedrive, dry: bool=True):
    redis_conn = get_redis_connection()
    q = Queue(name="worker", connection=redis_conn)
    job = q.enqueue(find_person_in_pipedrive, request.model_dump(), dry)
    return job.id

@router.post("/test_db_add")
def add_row_to_executions(request: FindPersonInPipedrive):
    new_execution_data = new_execution(next(get_db()), request.model_dump())
    return new_execution_data

@router.post("/get_executions")
def get_executions_from_db(execution_success: Optional[bool] = None, range: Optional[List[str]] = None, current_user: UserAuth = Depends(get_current_user)):
    # date hase to be in "yyyy-mm-dd" format
    db = next(get_db())
    query = db.query(Execution)
    if execution_success != None:
        query = query.filter(Execution.Execution_success == execution_success)
    if range:
        start_date = datetime.fromisoformat(range[0]).date()
        if len(range) == 1:
            end_date = datetime.now().date()
        elif len(range) == 2:
            end_date = datetime.fromisoformat(range[1]).date()
        query = query.filter(cast(Execution.Timestamp, Date) >= start_date,
                                 cast(Execution.Timestamp, Date) <= end_date)
    data = query.all()
    db.close()
    return data

@router.post("/run_failed")
def run_find_person_failed_executions_in_queue(list_of_IDs: List[int], dry: bool=True, current_user: UserAuth = Depends(get_current_user)):
    db = next(get_db())
    redis_conn = get_redis_connection()
    q = Queue(name="worker", connection=redis_conn)
    list_of_job_ids = []
    for ID in list_of_IDs:
        row = db.query(Execution).filter(Execution.ID == ID).first()
        job = q.enqueue(find_person_in_pipedrive, row.Input_json, dry)
        list_of_job_ids.append(job.id)
    db.close()
    return list_of_job_ids










