from fastapi import FastAPI, HTTPException, Request
from app.routers import items
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


app = FastAPI()
# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Only keep the custom message part of the error
    error_messages = [error['msg'].replace("Value error, ", "") for error in errors]
    return JSONResponse(
        status_code=422,
        content={"detail": error_messages}
    )

# Include the router
app.include_router(items.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app"}