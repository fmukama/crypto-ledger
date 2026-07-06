from fastapi import APIRouter, Depends

from blockchain import Blockchain

from ..dependencies import get_ledger
from ..schemas import TransactionIn

router = APIRouter(tags=["transactions"])


# User Story 2 -- Submit transactions

@router.post("/transactions", status_code=201)
def post_transaction(tx: TransactionIn, ledger: Blockchain = Depends(get_ledger)):
    """Queue a validated transaction in the mempool (201 Created)."""
    stored = ledger.add_transaction(tx.sender, tx.recipient, tx.amount)
    return {"message": "Transaction added to mempool.", "transaction": stored}


@router.get("/mempool")
def get_mempool(ledger: Blockchain = Depends(get_ledger)):
    """List transactions waiting to be mined."""
    return {"count": len(ledger.mempool), "pending": ledger.mempool}
