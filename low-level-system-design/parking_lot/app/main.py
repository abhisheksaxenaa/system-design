from fastapi import FastAPI
from sqlmodel import SQLModel
from app.db import engine
from app.api import router as api_router

app = FastAPI(title="Parking Lot API")
app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    # import models so SQLModel metadata is populated
    import app.models.models  # noqa: F401
    SQLModel.metadata.create_all(engine)
