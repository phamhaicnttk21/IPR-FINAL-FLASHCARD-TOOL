from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path
import pandas as pd

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the upload directory exists

@app.get("/home")
def access_homepage():
    return {"message": "Hello Group 3"}

@app.post("/home/uploadDoc")
async def upload_doc(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/vnd.ms-excel",  # .xls
    ]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files are allowed.")

    # Read file into Pandas DataFrame
    try:
        df = pd.read_excel(file.file)  # Read Excel file
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Excel file format.")

    # Ensure the file has exactly 2 columns: "meaning" and "word"
    required_columns = ["meaning", "word"]
    if list(df.columns) != required_columns:
        raise HTTPException(status_code=400, detail=f"Excel file must have exactly these columns: {required_columns}")

    # Ensure no null values in any row
    if df.isnull().values.any():
        raise HTTPException(status_code=400, detail="Each row must have non-empty values for 'meaning' and 'word'.")

    # Save the file after validation
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    return {"filename": file.filename, "status": "Uploaded successfully"}
