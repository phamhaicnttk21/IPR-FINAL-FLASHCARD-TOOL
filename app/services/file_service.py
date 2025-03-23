import pandas as pd
from fastapi import HTTPException, UploadFile
from pathlib import Path

def validate_and_save_file(file, upload_dir: Path):
    # Validate file type
    if file.content_type not in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/vnd.ms-excel",  # .xls
    ]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files are allowed.")

    # Read file into Pandas DataFrame
    try:
        df = pd.read_excel(file.file,engine="openpyxl")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Excel file format.")

    # Ensure the file has exactly 2 columns: "meaning" and "word"
    required_columns = ["Word", "Meaning"]
    if list(df.columns) != required_columns:
        raise HTTPException(status_code=400, detail=f"Excel file must have exactly these columns: {required_columns}")

    # Ensure no null values in any row
    if df.isnull().values.any():
        raise HTTPException(status_code=400, detail="Each row must have non-empty values for 'meaning' and 'word'.")

    # **Reset file pointer before saving**
    file.file.seek(0)

    # Save the file after validation
    file_path = upload_dir / file.filename
    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    return {"filename": file.filename, "status": "Uploaded successfully"}

def delete_file(filename: str, upload_dir: Path):
    file_path = upload_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        file_path.unlink()  # Delete file
        return {"filename": filename, "status": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")


def update_file(filename: str, updates: list, upload_dir: Path):
    file_path = upload_dir / filename

    # Check if file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        # Read existing file
        df = pd.read_excel(file_path, engine="openpyxl")

        # Ensure required columns exist
        required_columns = ["Word", "Meaning"]
        if list(df.columns) != required_columns:
            raise HTTPException(status_code=400, detail=f"Excel file must have exactly these columns: {required_columns}")

        # Convert updates to a DataFrame
        updates_df = pd.DataFrame(updates)

        # Ensure new data has correct columns
        if list(updates_df.columns) != required_columns:
            raise HTTPException(status_code=400, detail=f"Updates must contain columns: {required_columns}")

        # Append new data using pd.concat()
        df = pd.concat([df, updates_df], ignore_index=True)

        # Save back to the same file
        df.to_excel(file_path, index=False, engine="openpyxl")

        return {"filename": filename, "status": "Updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File update failed: {str(e)}")