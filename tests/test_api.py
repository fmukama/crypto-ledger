"""Integration tests (Sprint 1) -- exercise the HTTP layer via TestClient."""

import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client():
    """Fresh app + fresh chain per test => no state leaks between tests."""
    return TestClient(create_app())


# User Story 1: GET /chain

def test_get_chain_returns_200_with_genesis(client):
    response = client.get("/chain")
    assert response.status_code == 200
    body = response.json()
    assert body["length"] == 1
    assert body["chain"][0]["index"] == 0


# User Story 2: POST /transactions + GET /mempool

def test_post_valid_transaction_returns_201(client):
    response = client.post(
        "/transactions",
        json={"sender": "alice", "recipient": "bob", "amount": 5},
    )
    assert response.status_code == 201
    assert response.json()["transaction"]["amount"] == 5


def test_post_transaction_missing_field_returns_400(client):
    response = client.post("/transactions", json={"sender": "alice", "amount": 5})
    assert response.status_code == 400


def test_post_negative_amount_returns_400(client):
    response = client.post(
        "/transactions",
        json={"sender": "alice", "recipient": "bob", "amount": -1},
    )
    assert response.status_code == 400


def test_mempool_lists_pending_transactions(client):
    client.post("/transactions",
                json={"sender": "a", "recipient": "b", "amount": 1})
    response = client.get("/mempool")
    assert response.status_code == 200
    assert response.json()["count"] == 1


# User Story 3: POST /mine

def test_mine_returns_new_block_and_clears_mempool(client):
    client.post("/transactions",
                json={"sender": "a", "recipient": "b", "amount": 2})
    response = client.post("/mine")
    assert response.status_code == 200
    assert response.json()["block"]["index"] == 1
    assert client.get("/mempool").json()["count"] == 0


def test_mine_with_empty_mempool_returns_400(client):
    assert client.post("/mine").status_code == 400


# User Story 4: GET /blocks/{index} + GET /balance/{address}

def test_get_existing_block_returns_200(client):
    response = client.get("/blocks/0")
    assert response.status_code == 200
    assert response.json()["index"] == 0


def test_get_missing_block_returns_404(client):
    assert client.get("/blocks/999").status_code == 404


def test_balance_endpoint_aggregates_mined_transactions(client):
    client.post("/transactions",
                json={"sender": "a", "recipient": "b", "amount": 7})
    client.post("/mine")
    response = client.get("/balance/b")
    assert response.status_code == 200
    assert response.json()["balance"] == 7


# User Story 5: GET /health

def test_health_reports_status_and_telemetry(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["current_block_height"] == 0     # only genesis so far
    assert body["pending_mempool_size"] == 0


def test_health_telemetry_tracks_state_changes(client):
    client.post("/transactions",
                json={"sender": "a", "recipient": "b", "amount": 3})
    body = client.get("/health").json()
    assert body["pending_mempool_size"] == 1
    client.post("/mine")
    body = client.get("/health").json()
    assert body["current_block_height"] == 1
    assert body["pending_mempool_size"] == 0
