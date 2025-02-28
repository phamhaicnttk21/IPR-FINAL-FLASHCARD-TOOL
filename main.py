from fastapi import FastAPI

app = FastAPI();

@app.get("/")
def access_homepage():
    return {"Hello Group 3"}