from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.schemas import IdentifyRequest, ContactResponse
from app.services import identify


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB connectivity
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    yield
    # Shutdown
    engine.dispose()


app = FastAPI(title="Bitespeed Identity Reconciliation", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/identify", response_model=ContactResponse)
def identify_endpoint(request: IdentifyRequest, db: Session = Depends(get_db)):
    return identify(db, request)
