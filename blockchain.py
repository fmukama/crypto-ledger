import hashlib
import json
import logging

logger = logging.getLogger("ledger.core")


class Blockchain:
    """In-memory, single-node blockchain plus a mempool of pending transactions."""

    def __init__(self):
        self.chain = []      # list of mined blocks (dicts)
        self.mempool = []    # pending transactions waiting to be mined
        self._create_genesis_block()

    # User Story 1 -- Block construction & hashing

    def _create_genesis_block(self):
        """Create the hardcoded first block (index 0). Runs once at startup.

        The genesis block has no parent, so previous_hash is 64 zeros.
        A FIXED timestamp (0) makes its hash deterministic and testable.
        """
        genesis = {
            "index": 0,
            "timestamp": 0,
            "transactions": [],
            "previous_hash": "0" * 64,
            "nonce": 0,
        }
        genesis["hash"] = self.hash_block(genesis)
        self.chain.append(genesis)
        logger.info("Genesis block created (hash=%s...)", genesis["hash"][:16])

    @staticmethod
    def hash_block(block):
        """Return the SHA-256 hex digest of a block's content.

        1. Drop the 'hash' key (a hash cannot include itself).
        2. json.dumps with sort_keys=True -> canonical byte string, so the
           SAME content always produces the SAME digest.
        3. Any tampering with any field changes the digest completely
           (avalanche effect of SHA-256).
        """
        content = {key: value for key, value in block.items() if key != "hash"}
        encoded = json.dumps(content, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    # User Story 2 -- Submit transactions to the mempool

    def add_transaction(self, sender, recipient, amount):
        """Validate a transaction and queue it in the mempool.

        Raises ValueError on bad input; the API layer maps that to HTTP 400.
        Returns the stored transaction dict on success.
        """
        if not sender or not recipient:
            raise ValueError("Both 'sender' and 'recipient' are required.")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise ValueError("'amount' must be a number.")
        if amount <= 0:
            raise ValueError("'amount' must be a positive number.")

        transaction = {"sender": sender, "recipient": recipient, "amount": amount}
        self.mempool.append(transaction)
        logger.info("TX queued: %s -> %s (amount=%s). Mempool size=%d",
                    sender, recipient, amount, len(self.mempool))
        return transaction