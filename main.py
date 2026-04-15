from fastapi import FastAPI
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def read_health():
    return {"status": "ok"}
