import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from blockchain import Blockchain

logger = logging.getLogger("ledger.api")

APP_VERSION = "1.0.0"


class TransactionIn(BaseModel):
    """Schema for POST /transactions."""
    sender: str = Field(min_length=1, examples=["alice"])
    recipient: str = Field(min_length=1, examples=["bob"])
    amount: float = Field(gt=0, examples=[25.0])
