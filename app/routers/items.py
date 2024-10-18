from fastapi import APIRouter,HTTPException
from app.models import item_model
from app.database import item_collection, item_helper
from bson import ObjectId


router = APIRouter()

@router.get("/items/")
def getItems():
    items = item_collection.find()
    listItems = list(items)
    for item in listItems:
        item['_id'] = str(item['_id'])
        
    return listItems

@router.post("/additems/")
def addItems(items:item_model.Item):
    itemDictinory = dict(items)
    itemInsert = item_collection.insert_one(itemDictinory)
    if itemInsert:
        items = item_collection.find_one(itemInsert.inserted_id)
        return item_helper(items)
     
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/getitem/{itemID}")
def selectedItem(itemID:str):
    item = item_collection.find_one({"_id":ObjectId(itemID)})
    print(item)
    if item :
        item['_id'] = str(item['_id'])
        return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.patch("/updateitem/{itemID}")
def updateItems(itemID:str,items:item_model.Item):
    itemDictinory = dict(items)
    updateitem = item_collection.update_one({"_id": ObjectId(itemID)}, {"$set": itemDictinory})
    if updateitem.modified_count == 1:
        item = item_collection.find_one({"_id": ObjectId(itemID)})
        return item_helper(item)
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/deleteitem/{itemID}")
def deleteItem(itemID:str):
    deleteData = item_collection.delete_one({"_id":ObjectId(itemID)})
    if deleteData.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")


