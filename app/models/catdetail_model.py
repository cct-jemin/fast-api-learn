from pydantic import BaseModel, Field, field_validator
    
class CatDetail(BaseModel):
    category_id:str
    label: str
    type: bytearray
    unit:bytearray