import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from blockchain import Blockchain

logger = logging.getLogger("ledger.api")

APP_VERSION = "2.0.0"


class TransactionIn(BaseModel):
    """Schema for POST /transactions."""
    sender: str = Field(min_length=1, examples=["alice"])
    recipient: str = Field(min_length=1, examples=["bob"])
    amount: float = Field(gt=0, examples=[25.0])


def create_app() -> FastAPI:
    """Application factory: every call builds a FRESH app with a FRESH chain.
    Tests use this to get full isolation between test cases."""
    app = FastAPI(title="Single-Node Cryptographic Ledger", version=APP_VERSION)
    ledger = Blockchain()

    # FastAPI returns 422 for schema violations by default; our Acceptance
    # Criteria demand 400 Bad Request, so we override the handler.

    @app.exception_handler(RequestValidationError)
    async def validation_to_400(request: Request, exc: RequestValidationError):
        details = [{"field": ".".join(str(part) for part in err["loc"]),
                    "issue": err["msg"]} for err in exc.errors()]
        logger.warning("Rejected payload on %s: %s", request.url.path, details)
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request.", "details": details},
        )

    # User Story 1 -- View chain history

    @app.get("/chain")
    def get_chain():
        """Return the full block history (genesis included)."""
        return {"length": len(ledger.chain), "chain": ledger.chain}

    # User Story 2 -- Submit transactions

    @app.post("/transactions", status_code=201)
    def post_transaction(tx: TransactionIn):
        """Queue a validated transaction in the mempool (201 Created)."""
        stored = ledger.add_transaction(tx.sender, tx.recipient, tx.amount)
        return {"message": "Transaction added to mempool.", "transaction": stored}

    @app.get("/mempool")
    def get_mempool():
        """List transactions waiting to be mined."""
        return {"count": len(ledger.mempool), "pending": ledger.mempool}

    # User Story 3 -- Mine pending transactions  [Sprint 2]

    @app.post(
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
    def mine():
        """Run Proof-of-Work over the mempool and append the new block."""
        try:
            block = ledger.mine_block()
        except ValueError as exc:            # empty mempool -> client error
            logger.warning("Mining rejected: %s", exc)
            raise HTTPException(status_code=400, detail=str(exc))
        return {"message": "New block mined.", "block": block}

    return app


# Module-level app instance for `uvicorn main:app`
app = create_app()
