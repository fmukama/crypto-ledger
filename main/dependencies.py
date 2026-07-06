from fastapi import Request

from blockchain import Blockchain


def get_ledger(request: Request) -> Blockchain:
    """Resolve the per-app Blockchain instance stored on app.state.

    One instance per app (set in create_app), shared by every router.
    """
    return request.app.state.ledger
