"""Unit tests for blockchain.py (Sprint 1) -- pure domain logic, no HTTP."""

import pytest

from blockchain import Blockchain


@pytest.fixture
def ledger():
    """A fresh, isolated chain for every single test."""
    return Blockchain()

# User Story 1: genesis & hashing

def test_chain_starts_with_genesis_block(ledger):
    assert len(ledger.chain) == 1
    genesis = ledger.chain[0]
    assert genesis["index"] == 0
    assert genesis["previous_hash"] == "0" * 64


def test_genesis_hash_is_valid_sha256(ledger):
    # SHA-256 digests are exactly 64 hexadecimal characters.
    assert len(ledger.chain[0]["hash"]) == 64
    int(ledger.chain[0]["hash"], 16)   # raises ValueError if not valid hex


def test_hashing_is_deterministic(ledger):
    block = ledger.chain[0]
    assert Blockchain.hash_block(block) == Blockchain.hash_block(block)


# User Story 2: mempool validation

def test_valid_transaction_enters_mempool(ledger):
    ledger.add_transaction("alice", "bob", 25)
    assert len(ledger.mempool) == 1
    assert ledger.mempool[0] == {"sender": "alice", "recipient": "bob",             "amount": 25}


def test_negative_amount_is_rejected(ledger):
    with pytest.raises(ValueError):
        ledger.add_transaction("alice", "bob", -5)


def test_zero_amount_is_rejected(ledger):
    with pytest.raises(ValueError):
        ledger.add_transaction("alice", "bob", 0)


def test_missing_sender_is_rejected(ledger):
    with pytest.raises(ValueError):
        ledger.add_transaction("", "bob", 10)