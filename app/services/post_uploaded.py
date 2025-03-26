import pandas as pd
from pathlib import Path
import json
from fastapi import HTTPException, status

PROCESS_DIR = Path("processed")
PROCESS_DIR.mkdir(exist_ok=True)

#Lấy file duy nhất trong folder uploads
def get_single_file(folder_path="uploads"):
    try:
        folder = Path(folder_path)
        if not folder.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder Not Found")
        files = list(folder.iterdir())
        if len(files) == 1:
            return str(files[0])
        elif len(files) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empty Folder.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Folder has more than one file.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
    
file_path = get_single_file("uploads")   
    
#Chuyển dữ liệu thành dạng dictionary
def data_to_dict(file_path):
    try:
        file = Path(file_path)
        if not file.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File Not Found.")

        if file.suffix.lower() in [".xlsx", ".xls"]:
            data = pd.read_excel(file_path)
        elif file.suffix.lower() == ".csv":
            data = pd.read_csv(file_path)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File type is not supported")

        word_dict = dict(zip(data['Word'], data['Meaning']))
        return word_dict

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty or invalid.")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File does not contain 'Word' or 'Meaning' columns.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")
    

# Save file JSON
def save_dict_to_json(data_dict, file_name):
    try:
        file_path = PROCESS_DIR / f"{Path(file_name).stem}.json"
        with open(file_path, "w", encoding="utf-8") as f: #Thêm encoding utf-8
            json.dump(data_dict, f, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error saving JSON: {e}")
