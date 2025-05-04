from fastapi import FastAPI
from .database import engine, Base
from . import models
from . import crud

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "URL Shortener is alive"}

@app.post("/shorten")
def shorten_url(original_url: str):
    return crud.create_short_url(original_url)

@app.get("/r/{code}")
def redirect(code: str):
    return crud.resolve_short_url(code)
