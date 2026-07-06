import hashlib
import json
import logging
import time 

logger = logging.getLogger("ledger.core")

# Proof-of-Work target: a valid block hash must START with this prefix.
# Each extra hex zero multiplies the expected work by 16.
DIFFICULTY_PREFIX = "00"


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

    # User Story 3 -- Mining / Proof of Work [Sprint 2]

    def proof_of_work(self, block):
        """Increment the nonce until the block hash starts with DIFFICULTY_PREFIX.

        Math: a SHA-256 hex digest is uniform, so a single attempt succeeds
        with p = (1/16)^d where d = len(prefix). For '00', p = 1/256 and the
        attempt count follows a Geometric(p) distribution with E[attempts] =
        1/p = 256. Cheap enough for tests, real enough to demonstrate PoW.
        """
        attempts = 0
        started = time.perf_counter()

        block["nonce"] = 0
        candidate = self.hash_block(block)
        while not candidate.startswith(DIFFICULTY_PREFIX):
            block["nonce"] += 1
            attempts += 1
            candidate = self.hash_block(block)

        elapsed_ms = (time.perf_counter() - started) * 1000
        # Observability (Sprint 2 improvement): log the cost of every PoW run.
        logger.info("PoW solved: nonce=%d after %d attempts in %.2f ms",
                    block["nonce"], attempts, elapsed_ms)
        return candidate

    def mine_block(self):
        """Bundle the whole mempool into a new block, solve PoW, append, wipe.

        Raises ValueError if the mempool is empty (nothing to mine).
        Returns the newly appended block.
        """
        if not self.mempool:
            raise ValueError("Mempool is empty -- nothing to mine.")

        last_block = self.chain[-1]
        new_block = {
            "index": last_block["index"] + 1,
            "timestamp": time.time(),
            "transactions": list(self.mempool),      # snapshot of pending TXs
            "previous_hash": last_block["hash"],     # cryptographic link
            "nonce": 0,
        }
        new_block["hash"] = self.proof_of_work(new_block)

        self.chain.append(new_block)
        self.mempool = []   # Acceptance Criteria: mempool wiped after mining
        logger.info("Block #%d appended with %d transaction(s).",
                    new_block["index"], len(new_block["transactions"]))
        return new_block


    # User Story 4 -- Inspect blocks and balances [Sprint 2]
   
    def get_block(self, index):
        """Return the block at `index`, or None if it does not exist."""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None

    def get_balance(self, address):
        """Net balance = sum(received) - sum(sent) over all MINED blocks.

        Pending mempool transactions are intentionally excluded: they are
        not yet confirmed, so they must not affect a spendable balance.
        """
        balance = 0
        for block in self.chain:
            for tx in block["transactions"]:
                if tx["recipient"] == address:
                    balance += tx["amount"]
                if tx["sender"] == address:
                    balance -= tx["amount"]
        return balance

   
    # Chain integrity audit
   

    def is_valid(self):
        """Recompute every hash and verify each block links to its parent.

        Returns False if ANY block was tampered with or any link is broken.
        """
        for i in range(1, len(self.chain)):
            current, previous = self.chain[i], self.chain[i - 1]
            if current["previous_hash"] != previous["hash"]:
                logger.error("Broken link at block #%d", current["index"])
                return False
            if current["hash"] != self.hash_block(current):
                logger.error("Tampered content at block #%d", current["index"])
                return False
        return True
