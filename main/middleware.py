import logging
import time

from fastapi import Request

logger = logging.getLogger("ledger.api")


async def log_requests(request: Request, call_next):
    """Observability middleware (Sprint 2): log every request + latency."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %d (%.1f ms)", request.method,
                request.url.path, response.status_code, elapsed_ms)
    return response
