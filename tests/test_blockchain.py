"""Unit tests for blockchain.py (Sprint 1) -- pure domain logic, no HTTP."""

import pytest

from blockchain import Blockchain, DIFFICULTY_PREFIX


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


# User Story 3: mining / proof of work

def test_mining_empty_mempool_raises(ledger):
    with pytest.raises(ValueError):
        ledger.mine_block()


def test_mined_block_satisfies_difficulty(ledger):
    ledger.add_transaction("alice", "bob", 10)
    block = ledger.mine_block()
    assert block["hash"].startswith(DIFFICULTY_PREFIX)


def test_mining_links_block_and_wipes_mempool(ledger):
    ledger.add_transaction("alice", "bob", 10)
    block = ledger.mine_block()
    assert block["index"] == 1
    assert block["previous_hash"] == ledger.chain[0]["hash"]   # crypto link
    assert ledger.mempool == []                                # AC: wiped


# User Story 4: block/balance queries + integrity audit

def test_balance_aggregates_sent_and_received(ledger):
    ledger.add_transaction("alice", "bob", 30)
    ledger.add_transaction("bob", "carol", 10)
    ledger.mine_block()
    assert ledger.get_balance("bob") == 20      # +30 in, -10 out
    assert ledger.get_balance("alice") == -30
    assert ledger.get_balance("carol") == 10


def test_pending_transactions_do_not_affect_balance(ledger):
    ledger.add_transaction("alice", "bob", 99)   # queued, NOT mined
    assert ledger.get_balance("bob") == 0


def test_tampering_breaks_chain_validity(ledger):
    ledger.add_transaction("alice", "bob", 10)
    ledger.mine_block()
    assert ledger.is_valid()
    ledger.chain[1]["transactions"][0]["amount"] = 9999   # simulate attack
    assert not ledger.is_valid()
