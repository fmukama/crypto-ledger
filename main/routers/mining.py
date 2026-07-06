import logging

from fastapi import APIRouter, Depends, HTTPException

from blockchain import Blockchain

from ..dependencies import get_ledger

logger = logging.getLogger("ledger.api")

router = APIRouter(tags=["mining"])


# User Story 3 -- Mine pending transactions [Sprint 2]

@router.post(
    "/mine",
    responses={
        200: {
            "description": "New block mined.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "New block mined.",
                        "block": {
                            "index": 1,
                            "timestamp": 1783362316.0678701,
                            "transactions": [
                                {"sender": "alice", "recipient": "bob", "amount": 10.0}
                            ],
                            "previous_hash": "0" * 64,
                            "nonce": 137,
                            "hash": "0000" + "a" * 60,
                        },
                    }
                }
            },
        },
        400: {
            "description": "Mempool is empty.",
            "content": {
                "application/json": {
                    "example": {"detail": "Mempool is empty -- nothing to mine."}
                }
            },
        },
    },
)
def mine(ledger: Blockchain = Depends(get_ledger)):
    """Run Proof-of-Work over the mempool and append the new block."""
    try:
        block = ledger.mine_block()
    except ValueError as exc:            # empty mempool -> client error
        logger.warning("Mining rejected: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "New block mined.", "block": block}
