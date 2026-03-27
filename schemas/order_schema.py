from pydantic import BaseModel

class OrderCreate(BaseModel):

    user_id: int


class OrderDetailCreate(BaseModel):

    product_id: int
    qty: int