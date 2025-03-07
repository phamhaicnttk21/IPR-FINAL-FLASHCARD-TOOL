from fastapi import FastAPI
from app.routes.file_router import router as file_router

app = FastAPI()

# Include API routes
app.include_router(file_router, prefix="/home", tags=["File Operations"])

@app.get("/")
def home():
    return {"message": "Welcome to FlashCard Final Project GROUP 3"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
