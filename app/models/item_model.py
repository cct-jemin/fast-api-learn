from pydantic import BaseModel,Field
class Item(BaseModel):
    name: str = Field(..., min_length=1, description="The name of the item (must not be empty)")
    price: float = Field(..., gt=0, description="The price of the item (must be greater than 0)") 