import time

from fastapi import APIRouter, Depends, Request

from blockchain import Blockchain

from ..dependencies import get_ledger

router = APIRouter(tags=["health"])


# User Story 5 -- Node health telemetry [Sprint 2]

@router.get("/health")
def health(request: Request, ledger: Blockchain = Depends(get_ledger)):
    """Liveness + basic telemetry for monitoring tools."""
    return {
        "status": "healthy",
        "current_block_height": len(ledger.chain) - 1,
        "pending_mempool_size": len(ledger.mempool),
        "uptime_seconds": round(time.time() - request.app.state.started_at, 2),
        "version": request.app.state.version,
    }
