from pydantic import BaseModel, Field, field_validator
import json

with open('app/name_validate.json','r') as file:
    valid_data = json.load(file) 
    validNames = valid_data['valid_names']
    
class Item(BaseModel):
    name: str = Field(..., min_length=1, description="Name must be at least 1 character long.")
    price: float = Field(..., gt=0.0, description="Price must be greater than 0.")
    

    @field_validator("name", mode='before')
    def validate_name(cls, value):
        if len(value) < 1:
            raise ValueError("Name are required")
        else :
            if value not in validNames:
                raise ValueError("Name is not availabel in predefine set")
        return value

    @field_validator("price", mode='before')
    def validate_price(cls, value):

        if value <= 0:
            raise ValueError("Price must be greater than 0.")
        return value
    
    
