from fastapi import APIRouter, Depends, HTTPException

from blockchain import Blockchain

from ..dependencies import get_ledger

router = APIRouter(tags=["blocks"])


# User Story 4 -- Inspect blocks and balances [Sprint 2]

@router.get("/blocks/{index}")
def get_block(index: int, ledger: Blockchain = Depends(get_ledger)):
    """Return one block by index, or 404 if it does not exist."""
    block = ledger.get_block(index)
    if block is None:
        raise HTTPException(
            status_code=404,
            detail=f"Block {index} does not exist.",
        )
    return block


@router.get("/balance/{address}")
def get_balance(address: str, ledger: Blockchain = Depends(get_ledger)):
    """Net confirmed balance for an address (mined blocks only)."""
    return {"address": address, "balance": ledger.get_balance(address)}
