from pymongo import MongoClient
from bson import ObjectId
MONGO_DETAILS = "mongodb://localhost:27017" 

client = MongoClient(MONGO_DETAILS)
database = client.mydb  
item_collection = database.get_collection("items_collection")
category_collection = database.get_collection("category")
catdetail_collection = database.get_collection("catdetail")
notch_category_collection = database.get_collection("notch-category")
notch_sub_category_collection = database.get_collection("notch-sub-category")
v2_store = database.get_collection("v2_store")

# Helper function to convert MongoDB documents to JSON-friendly format
def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "price": item["price"],
    }