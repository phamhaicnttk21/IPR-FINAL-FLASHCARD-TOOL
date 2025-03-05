from fastapi import FastAPI
from app.routes import upload, delete  # Import routes

app = FastAPI()

# Include API routes
app.include_router(upload.router, prefix="/home", tags=["Upload"])
app.include_router(delete.router, prefix="/home", tags=["Delete"])

@app.get("/")
def home():
    return {"message": "Welcome to FlashCard Final Project GROUP 3"}
