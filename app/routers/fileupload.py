from fastapi import APIRouter,HTTPException,File, UploadFile,Query
import shutil
import os
import pandas as pd
import logging

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt"}
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
@router.post('/upload')
async def uploadFile(file:UploadFile=File(...)):
    uploadpath = "app/files/"
    filename = file.filename
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        logging.error(f"Invalid file extension for file '{filename}'")
        raise HTTPException(status_code=400,detail="Invalid extension upload only txt file") 
    try:
        if not os.path.exists(uploadpath):
            os.makedirs(uploadpath)
            
        file_location = os.path.join(uploadpath, file.filename)
        with open(file_location,'wb') as buffer:
          buffer.write(await file.read())  
          return {filename:filename,"message":"file uploaded successfully"}
    except Exception as e:
        logging.error(f"An error occurred while uploading file '{filename}': {e}")
        return {"error":str(e)}

@router.get('/readfile/')
async def readFile(filename:str = Query(..., min_length=1, max_length=100)):
    filepath = f"app/files/{filename}"
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        logging.error(f"Invalid file extension for file '{filename}'")
        raise HTTPException(status_code=400,detail="Invalid extension") 
    try:
        with open(filepath  , "r") as f:
            content = f.read()
        return {"filename": filename, "content": content}
    except FileNotFoundError:
        logging.error(f"File '{filename}' not found at path {filepath}")
        return {"error": "File not found"}
    except Exception as e:
        logging.error(f"An error occurred while reading file '{filename}': {e}")
        return {"error":str(e)}
    
@router.get('/writefile')
async def writeFile(message:str):
    try:
        filePath = f"app/files/test.txt"
        with open(filePath,"a") as f:
            f.write(message+'\n')
            return {"filename": 'test.txt', "content": message}
    except Exception as e:
        logging.error(f"an error to write test.txt file {e}")
        return {"error":str(e)}
    
@router.post('/getfile')
async def getFile(file:bytes=File(...)):
    content = file.decode('utf-8')  
    print(content) 
    lines = content.split('\n')  
    return {"content": lines}  
    
@router.post('/upload_option')
async def uploadOption(upload_file:UploadFile = File(...)):
    path = f"app/files/{upload_file.filename}"
    print(upload_file)
    with open(path,'wb') as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return {  
        'file': upload_file.filename,  
        'content': upload_file.content_type,  
        'path': path,  
    }
    
