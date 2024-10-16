from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"
    
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{itemId}")
async def itemGet(itemId:int,q:str|None=None,short:bool=False):
    item = {"item_id": itemId}
    if q:               
        item.update({"q":q})
        
    if not short:
        item.update({"description":"long message"})

    return item

@app.get("/readitems")
async def itemRead(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.get("/models/{modelName}")
async def modelGet(model_name:ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

@app.post("/books/")
async def createItems(items:Item):
    itemDictionary  = dict(items)
    if items.tax:
        priceWithTax = items.price + items.tax
        itemDictionary['withTax'] = priceWithTax
        
    return itemDictionary

@app.post("/books/{bookId}")
async def createItems(bookId:int,books:Item):
    return {"bookId": bookId, **books.dict()}
        
