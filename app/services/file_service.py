import pandas as pd
from fastapi import HTTPException, UploadFile
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUDIO_UPLOADFILE_DIR = Path("audio_uploadfile")
AUDIO_UPLOADFILE_DIR.mkdir(exist_ok=True)

def validate_and_save_file(file: UploadFile, upload_dir: Path):
    # Validate file extension
    if not file.filename.endswith('.xlsx'):
        logger.error(f"Invalid file extension: {file.filename}")
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed.")

    # Validate Excel MIME types
    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        logger.error(f"Invalid MIME type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only .xlsx files are allowed.")

    file_path = upload_dir / file.filename

    # Check if file already exists
    if file_path.exists():
        logger.warning(f"File already exists: {file.filename}")
        raise HTTPException(status_code=400, detail="File already exists.")

    try:
        # Save the file to disk first
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            logger.info(f"Saving file: {file.filename}, size: {len(content)} bytes")
            buffer.write(content)

        # Read the file from disk to validate
        df = pd.read_excel(file_path, engine="openpyxl")

        # Ensure the file has exactly 2 columns: "Word" and "Meaning"
        required_columns = ["Word", "Meaning"]
        if list(df.columns) != required_columns:
            file_path.unlink()  # Clean up the file if validation fails
            logger.error(f"Invalid columns: {list(df.columns)}")
            raise HTTPException(status_code=400, detail=f"Excel file must have exactly these columns: {required_columns}")

        # Ensure no null values in any row
        if df.isnull().values.any():
            file_path.unlink()  # Clean up the file
            logger.error("File contains null values")
            raise HTTPException(status_code=400, detail="Each row must have non-empty values for 'Word' and 'Meaning'.")

        return {"filename": file.filename, "status": "Uploaded successfully"}

    except Exception as e:
        if file_path.exists():
            file_path.unlink()  # Clean up if there's an error
        logger.error(f"File validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid Excel file format: {str(e)}")

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

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        df = pd.read_excel(file_path, engine="openpyxl")

        required_columns = ["Word", "Meaning"]
        if list(df.columns) != required_columns:
            raise HTTPException(status_code=400, detail=f"Excel file must have exactly these columns: {required_columns}")

        # Create a new DataFrame from the updates
        new_data = []
        for update in updates:
            # Access attributes directly since update is an UpdateItem object
            word = update.Word
            meaning = update.Meaning

            if not word or not meaning:  # Skip if either field is empty
                continue

            new_data.append({"Word": word, "Meaning": meaning})

        # Replace the existing DataFrame with the new data
        new_df = pd.DataFrame(new_data, columns=["Word", "Meaning"])

        # Save the updated DataFrame back to the file
        new_df.to_excel(file_path, index=False, engine="openpyxl")

        return {"filename": filename, "status": "Updated/Added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File update failed: {str(e)}")

def read_file_contents(filename: str, upload_dir: Path):
    file_path = upload_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        df = pd.read_excel(file_path, engine="openpyxl")

        required_columns = ["Word", "Meaning"]
        if list(df.columns) != required_columns:
            raise HTTPException(status_code=400, detail=f"Excel file must have exactly these columns: {required_columns}")

        # Convert DataFrame to list of dicts
        data = df.to_dict(orient="records")

        # Add audio file paths (look in audio_uploadfile for uploaded files)
        for item in data:
            word = item.get("Word", "")
            if word:
                safe_word = "".join(c if c.isalnum() else "_" for c in word)
                audio_path = AUDIO_UPLOADFILE_DIR / f"{safe_word}.mp3"
                if audio_path.exists():
                    item["audio_path"] = str(audio_path)
                else:
                    item["audio_path"] = None

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")