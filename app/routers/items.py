from fastapi import APIRouter,HTTPException
from app.models import item_model
from app.database import item_collection, item_helper
from bson import ObjectId


router = APIRouter()

@router.get("/items/")
def get_items():
    items = item_collection.find()
    listItems = list(items)
    for item in listItems:
        item['_id'] = str(item['_id'])
        
    return listItems

