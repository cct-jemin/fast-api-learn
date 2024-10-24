from fastapi import APIRouter,HTTPException,File, UploadFile
import shutil
import os
import pandas as pd

router = APIRouter()

# @router.post("/upload/")
# async def upload_file(file:UploadFile):
#     upload_dir = "app/files/"
#     if not os.path.exists(upload_dir):
#         os.makedirs(upload_dir)
#     file_location = os.path.join(upload_dir, file.filename)
#     with open(file_location,"wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
   
#     try:
#         df = pd.read_excel(file_location)
#         data = df.head().to_dict(orient="records")
#     except Exception as e:
#             return {"error":str(e)}
        
   
#     return  {"filename": file.filename,"content":data}

@router.get('/readfile/')
async def readFile(filename:str):
    filepath = f"app/files/{filename}"
    try:
        with open(filepath  , "r") as f:
            content = f.read()
        return {"filename": filename, "content": content}
    except FileNotFoundError:
        return {"error": "File not found"}
    except Exception as e:
        return {"error":str(e)}
    
