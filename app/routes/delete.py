from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads")


@router.delete("/deleteDoc")
async def delete_doc(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        file_path.unlink()  # Delete file
        return {"filename": filename, "status": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")
