from hashlib import sha256  # Importing the SHA-256 hashing algorithm
import json  # Importing JSON for data serialization
import time  # Importing time for timestamps
from flask import Flask, request  # Importing Flask and request for web framework functionality
import requests  # Importing requests for making HTTP requests

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        # Initializing a block with its index, transactions, timestamp, previous hash, and nonce
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """Returns the hash of the block contents."""
        block_string = json.dumps(self.__dict__, sort_keys=True)  # Convert block data to a JSON string
        return sha256(block_string.encode()).hexdigest()  # Return the SHA-256 hash of the block

class Blockchain:
    difficulty = 2  # Proof-of-Work difficulty level

    def __init__(self):
        self.unconfirmed_transactions = []  # List to hold pending transactions
        self.chain = []  # The blockchain ledger

    def create_genesis_block(self):
        """Generate the first block (genesis block) and add it to the chain."""
        genesis_block = Block(0, [], time.time(), "0")  # Create the genesis block
        genesis_block.hash = genesis_block.compute_hash()  # Compute its hash
        self.chain.append(genesis_block)  # Add it to the chain

    @property
    def last_block(self):
        return self.chain[-1]  # Return the last block in the chain

    def add_block(self, block, proof):
        """Validate and add a new block to the blockchain."""
        previous_hash = self.last_block.hash  # Get the hash of the last block

        if previous_hash != block.previous_hash:  # Check if the previous hash matches
            return False  # If not, return False

        if not Blockchain.is_valid_proof(block, proof):  # Validate the proof of work
            return False  # If invalid, return False

        block.hash = proof  # Set the block's hash to the proof
        self.chain.append(block)  # Add the block to the chain
        return True  # Return True if the block was added successfully

    @staticmethod
    def proof_of_work(block):
        """Find a valid nonce for Proof-of-Work."""
        block.nonce = 0  # Start with nonce set to 0
        computed_hash = block.compute_hash()  # Compute the initial hash
        
        # Keep incrementing nonce until a valid hash is found
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1  # Increment nonce
            computed_hash = block.compute_hash()  # Recompute hash
        
        return computed_hash  # Return the valid hash

    def add_new_transaction(self, transaction):
        """Add a new transaction to the unconfirmed transaction pool."""
        self.unconfirmed_transactions.append(transaction)  # Append the transaction to the pool

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """Verify that a block's hash meets the difficulty criteria."""
        return (block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash())  # Check validity

    @classmethod
    def check_chain_validity(cls, chain):
        """Verify the integrity of the blockchain."""
        previous_hash = "0"  # Initialize previous hash for the genesis block

        for block in chain:
            block_hash = block.hash  # Get the block's hash
            delattr(block, "hash")  # Temporarily remove the hash attribute

            # Validate the block and check the previous hash
            if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                return False  # Return False if invalid
            
            block.hash, previous_hash = block_hash, block_hash  # Restore hash and update previous hash

        return True  # Return True if all blocks are valid

    def mine(self):
        """Mine new transactions and add them to the blockchain."""
        if not self.unconfirmed_transactions:  # Check if there are unconfirmed transactions
            return False  # Return False if none

        last_block = self.last_block  # Get the last block
        new_block = Block(
            index=last_block.index + 1,  # Set index for the new block
            transactions=self.unconfirmed_transactions,  # Set transactions
            timestamp=time.time(),  # Set current timestamp
            previous_hash=last_block.hash  # Set previous hash
        )

        proof = self.proof_of_work(new_block)  # Find proof of work for the new block
        self.add_block(new_block, proof)  # Add the new block to the chain
        self.unconfirmed_transactions = []  # Clear the unconfirmed transactions

        return True  # Return True if mining was successful

# Flask application for Blockchain API
app = Flask(__name__)  # Create a Flask application instance

# Create Blockchain instance
blockchain = Blockchain()  # Instantiate the Blockchain
blockchain.create_genesis_block()  # Create the genesis block

# Store registered nodes for decentralization
peers = set()  # Set to hold registered peers

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    """Endpoint to submit a new transaction (vote)."""
    tx_data = request.get_json()  # Get transaction data from the request
    required_fields = ["voter_id", "party"]  # Define required fields

    # Check if all required fields are present
    if not all(field in tx_data for field in required_fields):
        return "Invalid transaction data", 400  # Return error if invalid

    tx_data["timestamp"] = time.time()  # Add timestamp to transaction data
    blockchain.add_new_transaction(tx_data)  # Add transaction to the blockchain

    return "Transaction added", 201  # Return success response

@app.route('/chain', methods=['GET'])
def get_chain():
    """Endpoint to retrieve the blockchain."""
    chain_data = [block.__dict__ for block in blockchain.chain]  # Serialize the blockchain
    return json.dumps({"length": len(chain_data), "chain": chain_data, "peers": list(peers)})  # Return chain data

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    """Endpoint to mine pending transactions."""
    if blockchain.mine():  # Attempt to mine transactions
        consensus()  # Call consensus to ensure chain integrity
        announce_new_block(blockchain.last_block)  # Announce the newly mined block
        return f"Block #{blockchain.last_block.index} mined.", 200  # Return success message
    return "No transactions to mine", 400  # Return error if no transactions

@app.route('/register_node', methods=['POST'])
def register_new_peers():
    """Endpoint to add new nodes to the network."""
    node_address = request.get_json().get("node_address")  # Get node address from request
    
    if not node_address:  # Check if node address is provided
        return "Invalid data", 400  # Return error if invalid

    peers.add(node_address)  # Add the new peer to the set
    return get_chain()  # Return the current chain

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """Register this node with an existing network."""
    node_address = request.get_json().get("node_address")  # Get node address from request

    if not node_address:  # Check if node address is provided
        return "Invalid data", 400  # Return error if invalid

    data = {"node_address": request.host_url}  # Prepare data for registration
    headers = {'Content-Type': "application/json"}  # Set headers for the request

    # Send registration request to the specified node
    response = requests.post(f"{node_address}/register_node", data=json.dumps(data), headers=headers)

    if response.status_code == 200:  # Check if registration was successful
        global blockchain, peers  # Declare global variables
        chain_dump = response.json()['chain']  # Get the chain from the response
        blockchain = create_chain_from_dump(chain_dump)  # Recreate the blockchain
        peers.update(response.json()['peers'])  # Update the peers set
        return "Registration successful", 200  # Return success message
    else:
        return response.content, response.status_code  # Return error response

def create_chain_from_dump(chain_dump):
    """Reconstruct blockchain from a dump of blocks."""
    generated_blockchain = Blockchain()  # Create a new Blockchain instance
    generated_blockchain.create_genesis_block()  # Create the genesis block

    for idx, block_data in enumerate(chain_dump):  # Iterate through the dumped chain
        if idx == 0:
            continue  # Skip genesis block

        # Create a new block from the dumped data
        block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], block_data["nonce"])
        proof = block_data['hash']  # Get the proof from the dumped data
        added = generated_blockchain.add_block(block, proof)  # Attempt to add the block

        if not added:  # Check if the block was added successfully
            raise Exception("Invalid chain data")  # Raise an exception if invalid

    return generated_blockchain  # Return the reconstructed blockchain

@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    """Verify and add a block mined by another node."""
    block_data = request.get_json()  # Get block data from the request
    block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], block_data["nonce"])  # Create a new block
    
    proof = block_data['hash']  # Get the proof from the request
    added = blockchain.add_block(block, proof)  # Attempt to add the block

    if not added:  # Check if the block was added successfully
        return "The block was rejected", 400  # Return error if rejected

    return "Block added", 201  # Return success message

@app.route('/pending_tx', methods=['GET'])
def get_pending_tx():
    """Retrieve unconfirmed transactions."""
    return json.dumps(blockchain.unconfirmed_transactions)  # Return unconfirmed transactions as JSON

def consensus():
    """Implement a simple consensus algorithm."""
    global blockchain  # Declare global blockchain variable
    longest_chain = None  # Variable to hold the longest chain found
    current_len = len(blockchain.chain)  # Get the current length of the blockchain

    for node in peers:  # Iterate through all registered peers
        response = requests.get(f"{node}/chain")  # Request the chain from the peer
        length = response.json()['length']  # Get the length of the chain
        chain = response.json()['chain']  # Get the chain data

        # Check if the received chain is longer and valid
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length  # Update current length
            longest_chain = chain  # Update longest chain

    if longest_chain:  # If a longer chain was found
        blockchain = create_chain_from_dump(longest_chain)  # Update the blockchain
        return True  # Return True indicating success
    return False  # Return False if no longer chain was found

def announce_new_block(block):
    """Broadcast new block to network peers."""
    for peer in peers:  # Iterate through all registered peers
        url = f"{peer}/add_block"  # Prepare the URL for adding the block
        headers = {'Content-Type': "application/json"}  # Set headers for the request
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)  # Send the block to the peer

# Uncomment to specify the port manually
app.run(debug=True, port=8000)  # Run the Flask application
