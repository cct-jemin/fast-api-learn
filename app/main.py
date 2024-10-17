from fastapi import FastAPI
from app.routers import items

app = FastAPI()


# Include the router
app.include_router(items.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app"}