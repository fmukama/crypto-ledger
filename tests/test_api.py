"""Integration tests (Sprint 1) -- exercise the HTTP layer via TestClient."""

import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client():
    """Fresh app + fresh chain per test => no state leaks between tests."""
    return TestClient(create_app(   ))

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
    response = client.post("/transactions",json={"sender": "alice", "amount": 5})
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