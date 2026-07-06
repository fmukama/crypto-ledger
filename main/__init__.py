from .app import APP_VERSION, create_app

__all__ = ["APP_VERSION", "app", "create_app"]

# Module-level app instance for `uvicorn main:app`
app = create_app()
