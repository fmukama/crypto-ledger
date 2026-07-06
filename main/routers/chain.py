from fastapi import APIRouter, Depends

from blockchain import Blockchain

from ..dependencies import get_ledger

router = APIRouter(tags=["chain"])


# User Story 1 -- View chain history

@router.get("/chain")
def get_chain(ledger: Blockchain = Depends(get_ledger)):
    """Return the full block history (genesis included)."""
    return {"length": len(ledger.chain), "chain": ledger.chain}
