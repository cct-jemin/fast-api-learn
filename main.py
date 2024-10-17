from fastapi import FastAPI,Query,Depends,Request
from enum import Enum
from pydantic import BaseModel
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
import time


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    
class User(BaseModel):
    username: str
    full_name: str | None = None

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{itemId}")
async def itemGet(itemId:int,q: Annotated[str | None, Query(min_length=3, max_length=50, regex="^fixedquery$")]=None,short:bool=False):
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

@app.get('/itemlist')
async def itemList(q:Annotated[str|None,Query(title="Query string", min_length=3)] = None):
    query = {"q":q}
    return query

@app.post('/addtest')
async def checkMultiData(item:Item,user:User):
    query = {"item":item,"user":user}
    return query
    
@app.get("/tokencheck/")
async def read_token(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
        
