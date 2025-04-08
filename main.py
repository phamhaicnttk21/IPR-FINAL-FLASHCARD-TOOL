<<<<<<< Updated upstream
from fastapi import FastAPI
from app.routes.file_router import router as file_router
#from pyngrok import ngrok

app = FastAPI()

# Include API routes with prefix
app.include_router(file_router, prefix="/home", tags=["File Operations"])

@app.get("/")
def home():
    return {"message": "Welcome to FlashCard Final Project GROUP 3"}

if __name__ == "__main__":
    import uvicorn

    # Set the new, valid ngrok authtoken
    #ngrok.set_auth_token("2uoe8xe7pjrLlcD5iEvC2kto9Ne_6KdnTYQ9RpMFtgkfuwbxa")

    # Start ngrok tunnel
    #public_url = ngrok.connect(8000)
    #print(f"Ngrok Public URL: {public_url}")

    # Run the app
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
=======
from fastapi import FastAPI
from app.routes.file_router import router as file_router

app = FastAPI()

# Include API routes
app.include_router(file_router, prefix="", tags=["File Operations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
>>>>>>> Stashed changes
