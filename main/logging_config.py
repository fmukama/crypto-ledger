import logging


def configure_logging():
    """One log format for the whole app (Sprint 2 improvement)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )
