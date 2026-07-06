from pydantic import BaseModel, Field


class TransactionIn(BaseModel):
    """Schema for POST /transactions."""
    sender: str = Field(min_length=1, examples=["alice"])
    recipient: str = Field(min_length=1, examples=["bob"])
    amount: float = Field(gt=0, examples=[25.0])
