from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import prompt_router
from app.routes.file_router import router as file_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default port
        "http://localhost:5173",  # Vite default port (if using Vite)
        "http://localhost",       # Catch-all for local testing
        "https://generally-known-civet.ngrok-free.app",  # Ngrok URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with prefix
app.include_router(file_router, prefix="/home", tags=["File Operations"])
app.include_router(prompt_router.router, prefix="/home", tags=["Prompt Operations"])

@app.get("/")
def home():
    return {"message": "Welcome to FlashCard Final Project GROUP 3"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)