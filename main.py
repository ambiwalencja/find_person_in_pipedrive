from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import find_person_endpoints, users_endpoints
from dotenv import load_dotenv
import os
from db.db_connect import engine
from db_models import execution


# running locally: uvicorn main:app --reload

if os.name == "nt":
    load_dotenv()

app = FastAPI(
    title="Automations",
    description="Automations API",
    version="0.1",
    # lifespan=lifespan
)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(find_person_endpoints.router)
app.include_router(users_endpoints.router)

@app.get("/")
def root():
    return "Automations API"

# create tables when starting program
execution.Base.metadata.create_all(engine)