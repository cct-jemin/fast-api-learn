from fastapi import APIRouter,HTTPException,File, UploadFile,Query
import shutil
import os
import pandas as pd
import logging
import json
# from app.models import category_model,catdetail_model
from app.database import category_collection,catdetail_collection,notch_category_collection
import pydash
from pprint import pprint


router = APIRouter()

ALLOWED_EXTENSIONS = {".txt",".xlsx"}
with open('app/sheet_validate.json','r') as file:
    sheet_data = json.load(file) 
    
with open('app/main_sheet.json','r') as mainfile:
    main_sheet_data = json.load(mainfile) 
    
    
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
    with open(path,'wb') as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    validation_errors = []    
    try :
        content = {}
        excel_data = pd.ExcelFile(path)
        sheet_names = excel_data.sheet_names
        for sheet in sheet_names:
            sheet_error = None
            #Sheet name validation
            if sheet not in ALLOWED_SHEET_NAMES:
                sheet_error = f"Invalid sheet name found: {sheet}"
                logging.error(f"Invalid sheet name found: {sheet}")
                validation_errors.append(sheet_error)
                continue  
                # raise HTTPException(status_code=400, detail=f"Invalid sheet name: {sheet}")
            df = excel_data.parse(sheet)
            df = df.fillna(value="")
            actual_headers = list(df.columns)
            
            #Header validation
            expectedHeader = sheet_data[sheet]['headers']
            invalid_headers = [header for header in actual_headers if header not in expectedHeader]   
            if invalid_headers:
                sheet_error = f"Invalid headers: {invalid_headers} in {sheet}."
                validation_errors.append(sheet_error)
                continue  
            
            #Record validation
            content[sheet] = df.to_dict(orient='records')
            for row_num, sheetContent in enumerate(content[sheet], start=1):
                if sheet == "Sheet1":
                    category = sheetContent['Category']
                    catDetail = category_collection.aggregate([
                        {
                            "$lookup": {
                                "from": "catdetail",
                                "let": { "categoryIdStr": { "$toString": "$_id" } }, 
                                "pipeline": [
                                    {
                                        "$match": {
                                            "$expr": { "$eq": ["$category_id", "$$categoryIdStr"] }  
                                        }
                                    }
                                ],
                                "as": "catdetail"
                            }
                        },
                        {
                            "$project": {
                                "name": 1,
                                "catdetail.label": 1,
                                "catdetail.type": 1,
                                "catdetail.unit": 1
                            }
                        }
                    ])
                    output = {}
                    for categoryData in catDetail:
                        category_name = categoryData["name"]
                        if categoryData["catdetail"]: 
                            cat_detail = categoryData["catdetail"][0] 
                            output[category_name] = {
                                "label": cat_detail["label"],
                                "type": cat_detail["type"],
                                "Unit": cat_detail["unit"]
                            }
                            
                    configData = output
                
                    if category not in configData:
                        validation_errors.append(f"Invalid Category '{category}' in {sheet} at row {row_num}.")
                        continue
                    
                    # Validate Type field
                    valid_types = configData[category]["type"]
                    record_type = sheetContent.get("Type")
                    if record_type not in valid_types:
                        validation_errors.append(f"Invalid Type '{record_type}' for Category '{category}' in {sheet} at row {row_num}.")

                    # Validate Unit field
                    valid_units = configData[category]["Unit"]
                    record_unit = sheetContent.get("Unit")
                    if record_unit not in valid_units:
                        validation_errors.append(f"Invalid Unit '{record_unit}' for Category '{category}' in {sheet} at row {row_num}.")
            
                
          
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"error in script: {e}"
        )
        
    if validation_errors:
        raise HTTPException(
            status_code=400,
            detail=f"Validation errors: {', '.join(validation_errors)}"
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
    
    
@router.post('/category-upload')
async def uploadCategory(upload_file:UploadFile = File(...)):
    path = f"app/files/{upload_file.filename}"
    ALLOWED_SHEET_NAMES = list(main_sheet_data.keys())
    with open(path,'wb') as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    validation_errors = []    
    try :
        content = {}
        excel_data = pd.ExcelFile(path)
        sheet_names = excel_data.sheet_names
        for sheet in sheet_names:
            sheet_error = None
            #Sheet name validation
            if sheet not in ALLOWED_SHEET_NAMES:
                sheet_error = f"Invalid sheet name found: {sheet}"
                logging.error(f"Invalid sheet name found: {sheet}")
                validation_errors.append(sheet_error)
                continue  
                # raise HTTPException(status_code=400, detail=f"Invalid sheet name: {sheet}")
            df = excel_data.parse(sheet)
            df = df.fillna(value="")
            actual_headers = list(df.columns)
            
            #Header validation
            expectedHeader = main_sheet_data[sheet]['headers']
            invalid_headers = [header for header in actual_headers if header not in expectedHeader]   
            if invalid_headers:
                sheet_error = f"Invalid headers: {invalid_headers} in {sheet}."
                validation_errors.append(sheet_error)
                continue  
            
            #Record validation
            content[sheet] = df.to_dict(orient='records')
            if sheet == "Sheet1":
                catDetail = notch_category_collection.aggregate([
                    {
                        "$lookup": {
                            "from": "notch-sub-category",
                            "let": { "categoryIdStr": { "$toString": "$_id" } }, 
                            "pipeline": [
                                {
                                    "$match": {
                                        "$expr": { "$eq": ["$category_id", "$$categoryIdStr"] }  
                                    }
                                }
                            ],
                            "as": "catdetail"
                        }
                    },
                    {
                        "$project": {
                            "category_name": 1,
                            "label":1,
                            "catdetail.sub_cat_name":1,
                            "catdetail.label": 1,
                            "catdetail.type": 1,
                            "catdetail.unit": 1
                        }
                    }
                ])
                
                pprint(catDetail)
                output = {}
                for categoryData in catDetail:
                    category_name = categoryData["category_name"]
                    if categoryData["catdetail"]: 
                        cat_detail = categoryData["catdetail"]
                        output[category_name] = {  "label": categoryData["label"]}
                        output[category_name]['attributeSubCategory'] = {}
                        for subCategoryData in cat_detail:
                            output[category_name]['attributeSubCategory'][subCategoryData["sub_cat_name"]] = {
                                "type": subCategoryData["type"],
                                "label": subCategoryData["label"]
                            }
                            
                for row_num, sheetContent in enumerate(content[sheet], start=1):
                    category = sheetContent['Category']
                    subcategory = sheetContent['Sub-cat']        
                    configData = output
                    # configData = main_sheet_data[sheet]["data"]
                    catlabels = [value['label'] for key, value in configData.items() if 'label' in value]
                    if category not in catlabels:
                        validation_errors.append(f"Invalid Category '{category}' in {sheet} at row {row_num}.")
                        continue
                    
                    # Validate SubCategory field
                    camelCaseCategory = pydash.strings.camel_case(category)
                    if subcategory not in  main_sheet_data[sheet]["data"][camelCaseCategory]["attributeSubCategory"]:
                        validation_errors.append(f"Invalid sub Category '{subcategory}' for Category '{category}' in {sheet} at row {row_num}.")
                        continue
                    
                    # Validate Type field
                    valid_types = configData[camelCaseCategory]['attributeSubCategory'][subcategory]['type']
                    record_type = sheetContent.get("Type")
                    if record_type not in valid_types:
                        validation_errors.append(f"Invalid Type '{record_type}' for Category '{category}' and Sub category '{subcategory}' in {sheet} at row {row_num}.")

            
                
          
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"error in script: {e}"
        )
        
    if validation_errors:
        raise HTTPException(
            status_code=400,
            detail=f"Validation errors: {', '.join(validation_errors)}"
        )
        
    return {  
        'file': upload_file.filename,  
        'content': upload_file.content_type,  
        'path': path,  
    }