from fastapi import FastAPI
from database import connection, cursor

app = FastAPI()

@app.get("/")
def home():
    return {
    "message": "Personal Finance Management API"
    }
