from fastapi import APIRouter,HTTPException,File, UploadFile,Query
import shutil
import os
import pandas as pd
import logging
import json

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt",".xlsx"}
with open('app/sheet_validate.json','r') as file:
    sheet_data = json.load(file) 
    
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
    fileSize = file.size
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        logging.error(f"Invalid file extension for file '{filename}'")
        raise HTTPException(status_code=400,detail="Invalid extension upload only txt file") 
    elif fileSize > 2 * 1024 * 1024:
        logging.error(f"file size too large. Max size is 2 MB.")
        raise HTTPException(status_code=400,detail="File size too large. Max size is 2 MB.") 
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
        if filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(filepath)
            df = df.fillna(value="")
            content = df.to_dict(orient="records")
        elif filename.endswith((".txt")):
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
    ALLOWED_SHEET_NAMES = list(sheet_data.keys())
    print(ALLOWED_SHEET_NAMES)
    with open(path,'wb') as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    try :
        excel_data = pd.ExcelFile(path)
        sheet_names = excel_data.sheet_names
        for sheet in sheet_names:
            #sheet name validation
            if sheet not in ALLOWED_SHEET_NAMES:
                logging.error(f"Invalid sheet name found: {sheet}")
                raise HTTPException(status_code=400, detail=f"Invalid sheet name: {sheet}")
            
            df = excel_data.parse(sheet)
            df = df.fillna(value="")
            actual_headers = list(df.columns)
            
            #header validation
            expectedHeader = sheet_data[sheet]['headers']
            print(expectedHeader)
            invalid_headers = [header for header in actual_headers if header not in expectedHeader]   
            if invalid_headers:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid headers: {invalid_headers} in {sheet}."
                )
          
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during header validation: {e}"
        )
        
    return {  
        'file': upload_file.filename,  
        'content': upload_file.content_type,  
        'path': path,  
    }
    
@router.get('/read-multisheet-file/')
async def readMultisheetFile(filename:str = Query(..., min_length=1, max_length=100)):
    filepath = f"app/files/{filename}"
    ALLOWED_SHEET_NAMES = {"Sheet1", "Sheet2", "Summary"}
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        logging.error(f"Invalid file extension for file '{filename}'")
        raise HTTPException(status_code=400,detail="Invalid extension") 
    try:
        if filename.endswith((".xlsx", ".xls")):
            excel_data = pd.ExcelFile(filepath)
            sheet_names = excel_data.sheet_names
            content = {}
            for sheet in sheet_names:
                df = excel_data.parse(sheet)
                df = df.fillna(value="")
                content[sheet] = df.to_dict(orient='records')
        elif filename.endswith((".txt")):
            with open(filepath  , "r") as f:
                content = f.read()
        return {"filename": filename, "content": content}
    except FileNotFoundError:
        logging.error(f"File '{filename}' not found at path {filepath}")
        return {"error": "File not found"}
    except Exception as e:
        logging.error(f"An error occurred while reading file '{filename}': {e}")
        return {"error":str(e)}