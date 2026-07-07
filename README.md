# crypto-ledger

[![CI Pipeline](https://github.com/fmukama/crypto-ledger/actions/workflows/ci.yaml/badge.svg)](https://github.com/fmukama/crypto-ledger/actions/workflows/ci.yaml)

A single-node cryptographic ledger: an in-memory blockchain with a REST API
built on FastAPI. Transactions are queued in a mempool, then bundled into
blocks and mined with a simple Proof-of-Work (SHA-256 hash must start with
`00`). Each block links to its parent via `previous_hash`, so the chain can
be re-validated end to end to detect tampering.

## Endpoints

| Method | Path                | Description                                          |
|--------|---------------------|-------------------------------------------------------|
| GET    | `/chain`            | Full block history (genesis included)                |
| POST   | `/transactions`     | Queue a transaction (`sender`, `recipient`, `amount`) |
| GET    | `/mempool`          | List transactions waiting to be mined                 |
| POST   | `/mine`             | Mine the mempool into a new block (400 if empty)      |
| GET    | `/blocks/{index}`   | Fetch one block by index (404 if it doesn't exist)    |
| GET    | `/balance/{address}`| Net confirmed balance for an address (mined only)     |
| GET    | `/health`           | Liveness + telemetry (block height, mempool size, uptime, version) |

Interactive API docs are auto-generated at `/docs` (Swagger) and `/redoc`.

## Project structure

```
blockchain.py       # domain layer: hashing, mempool, PoW mining, balances, chain validation
main/                # API layer (FastAPI)
  app.py             # app factory: middleware, exception handling, router registration
  routers/           # one module per resource (chain, transactions, mining, blocks, health)
  schemas.py         # request/response models
  dependencies.py    # shared Blockchain instance via app.state
  middleware.py      # per-request logging
  logging_config.py  # shared logging format
tests/               # pytest suite (domain logic + HTTP layer)
```

## Running locally

Requires Python 3.11+.

```bash
python -m venv .venv
.venv/Scripts/activate        # on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv venv
uv pip install -r requirements.txt
uv run uvicorn main:app --reload
```

The API is then available at `http://localhost:8000` (docs at `/docs`).

## Tests & linting

```bash
pytest -v      # unit + integration tests
flake8 .       # style checks (same gate as CI)
```
