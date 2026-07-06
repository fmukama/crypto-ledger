import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from blockchain import Blockchain

from .logging_config import configure_logging
from .middleware import log_requests
from .routers import blocks, chain, health, mining, transactions

configure_logging()
logger = logging.getLogger("ledger.api")

APP_VERSION = "2.0.0"


def create_app() -> FastAPI:
    """Application factory: every call builds a FRESH app with a FRESH chain.
    Tests use this to get full isolation between test cases."""
    app = FastAPI(title="Single-Node Cryptographic Ledger", version=APP_VERSION)
    app.state.ledger = Blockchain()
    app.state.started_at = time.time()
    app.state.version = APP_VERSION

    app.middleware("http")(log_requests)

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

    app.include_router(chain.router)
    app.include_router(transactions.router)
    app.include_router(mining.router)
    app.include_router(blocks.router)
    app.include_router(health.router)

    return app
