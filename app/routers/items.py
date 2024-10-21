from fastapi import APIRouter,HTTPException
from app.models import item_model
from app.database import item_collection, item_helper
from bson import ObjectId
import pdb
from pymongo.errors import PyMongoError


router = APIRouter()

@router.get("/items/")
def getItems():
    try :
        items = item_collection.find().sort('name',-1)
        listItems = list(items)
        for item in listItems:
            item['_id'] = str(item['_id'])   
        return {
            "message": "Data found",
            "status": 200,
            "data": listItems
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "message": "Internal Server Error",
            "error": str(e)
        })
        
@router.post("/additems/")
def addItems(items:item_model.Item):
    try : 
        itemDictinory = items.dict()
        itemInsert = item_collection.insert_one(itemDictinory)
        if itemInsert.inserted_id:
            items = item_collection.find_one(itemInsert.inserted_id)
            return {
                "message": "Item added successfully",
                "status": 200,
                "data": item_helper(items)
            }
        
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "message": "Internal Server Error",
            "error": str(e)
        })

@router.get("/getitem/{itemid}")
def selectedItem(itemid:str):
    try :
        item = item_collection.find_one({"_id":ObjectId(itemid)})
        if item :
            return  {
                "message": "Item Found",
                "status": 200,
                "data": item_helper(item)
            }
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code = 500,detail = {
            "message": "Internal Server Error",
            "error": str(e)
        })
        

@router.patch("/updateitem/{itemid}")
def updateItems(itemid:str,items:item_model.Item):
    try :
        checkItem = item_collection.find_one({'_id':ObjectId(itemid)})
        if checkItem:
            itemDictinory = items.dict()
            updateitem = item_collection.update_one({"_id": ObjectId(itemid)}, {"$set": itemDictinory})
            if updateitem.modified_count == 1:
                item = item_collection.find_one({"_id": ObjectId(itemid)})
                return {
                "message": "Item update successfully",
                "status": 200,
                "data": item_helper(item)
            }
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code = 500,detail = {
            "message": "Internal Server Error",
            "error": str(e)
        })

@router.delete("/deleteitem/{itemid}")
def deleteItem(itemid:str):
    try:
        deleteData = item_collection.delete_one({"_id":ObjectId(itemid)})
        if deleteData.deleted_count == 1:
            return {
                "message": "Item deleted successfully",
                "status": 200,
            }
        raise HTTPException(status_code=404, detail="Item not found")
    except (ValueError, PyMongoError) as e:
        # Catch specific exceptions for better error handling
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch any other exceptions
        raise HTTPException(status_code = 500,detail = {
            "message": "Internal Server Error",
            "error": str(e)
        })

