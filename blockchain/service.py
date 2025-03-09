from hashlib import sha256
import json
import time
from flask import Flask, request
import requests

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """Returns the hash of the block contents."""
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    difficulty = 2  # Proof-of-Work difficulty level

    def __init__(self):
        self.unconfirmed_transactions = []  # Pending transactions
        self.chain = []  # The blockchain ledger

    def create_genesis_block(self):
        """Generate the first block (genesis block) and add it to the chain."""
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """Validate and add a new block to the blockchain."""
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """Find a valid nonce for Proof-of-Work."""
        block.nonce = 0
        computed_hash = block.compute_hash()
        
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        
        return computed_hash

    def add_new_transaction(self, transaction):
        """Add a new transaction to the unconfirmed transaction pool."""
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """Verify that a block's hash meets the difficulty criteria."""
        return (block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        """Verify the integrity of the blockchain."""
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                return False
            
            block.hash, previous_hash = block_hash, block_hash

        return True

    def mine(self):
        """Mine new transactions and add them to the blockchain."""
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.hash
        )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        return True

# Flask application for Blockchain API
app = Flask(__name__)

# Create Blockchain instance
blockchain = Blockchain()
blockchain.create_genesis_block()

# Store registered nodes for decentralization
peers = set()

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    """Endpoint to submit a new transaction (vote)."""
    tx_data = request.get_json()
    required_fields = ["voter_id", "party"]

    if not all(field in tx_data for field in required_fields):
        return "Invalid transaction data", 400

    tx_data["timestamp"] = time.time()
    blockchain.add_new_transaction(tx_data)

    return "Transaction added", 201

@app.route('/chain', methods=['GET'])
def get_chain():
    """Endpoint to retrieve the blockchain."""
    chain_data = [block.__dict__ for block in blockchain.chain]
    return json.dumps({"length": len(chain_data), "chain": chain_data, "peers": list(peers)})

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    """Endpoint to mine pending transactions."""
    if blockchain.mine():
        consensus()
        announce_new_block(blockchain.last_block)
        return f"Block #{blockchain.last_block.index} mined.", 200
    return "No transactions to mine", 400

@app.route('/register_node', methods=['POST'])
def register_new_peers():
    """Endpoint to add new nodes to the network."""
    node_address = request.get_json().get("node_address")
    
    if not node_address:
        return "Invalid data", 400

    peers.add(node_address)
    return get_chain()

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """Register this node with an existing network."""
    node_address = request.get_json().get("node_address")

    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    response = requests.post(f"{node_address}/register_node", data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain, peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        return response.content, response.status_code

def create_chain_from_dump(chain_dump):
    """Reconstruct blockchain from a dump of blocks."""
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()

    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # Skip genesis block

        block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)

        if not added:
            raise Exception("Invalid chain data")

    return generated_blockchain

@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    """Verify and add a block mined by another node."""
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], block_data["nonce"])
    
    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was rejected", 400

    return "Block added", 201

@app.route('/pending_tx', methods=['GET'])
def get_pending_tx():
    """Retrieve unconfirmed transactions."""
    return json.dumps(blockchain.unconfirmed_transactions)

def consensus():
    """Implement a simple consensus algorithm."""
    global blockchain
    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get(f"{node}/chain")
        length = response.json()['length']
        chain = response.json()['chain']

        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = create_chain_from_dump(longest_chain)
        return True
    return False

def announce_new_block(block):
    """Broadcast new block to network peers."""
    for peer in peers:
        url = f"{peer}/add_block"
        headers = {'Content-Type': "application/json"}
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)

# Uncomment to specify the port manually
app.run(debug=True, port=8000)
