from pydantic import BaseModel, Field, field_validator
    
class Category(BaseModel):
    name: str
    