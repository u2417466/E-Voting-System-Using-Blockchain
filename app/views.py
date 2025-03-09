import datetime
import json
import requests
from flask import render_template, redirect, request, flash
from app import app
from config import Config

# The node with which our application interacts (Blockchain Service)
CONNECTED_SERVICE_ADDRESS = Config.BLOCKCHAIN_URL
POLITICAL_PARTIES = ["Democratic Party", "Republican Party", "Socialist Party"]
VOTER_IDS = [
    'VOID001', 'VOID002', 'VOID003',
    'VOID004', 'VOID005', 'VOID006',
    'VOID007', 'VOID008', 'VOID009',
    'VOID010', 'VOID011', 'VOID012',
    'VOID013', 'VOID014', 'VOID015'
]

vote_check = []
posts = []

def fetch_posts():
    """
    Fetch the blockchain chain data and parse it for display.
    """
    get_chain_address = f"{CONNECTED_SERVICE_ADDRESS}/chain"
    response = requests.get(get_chain_address)

    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'], reverse=True)

@app.route('/')
def index():
    fetch_posts()  # Fetch posts from the blockchain

    # Prepare vote summary
    vote_summary = {}
    for post in posts:
        party = post["party"]
        if party in vote_summary:
            vote_summary[party] += 1
        else:
            vote_summary[party] = 1

    return render_template(
        'index.html',
        title='E-Voting System Using Blockchain',
        posts=posts,
        vote_summary=vote_summary,
        readable_time=timestamp_to_string,
        political_parties=POLITICAL_PARTIES,
        voter_ids=VOTER_IDS
    )

@app.route('/submit', methods=['POST'])
def submit_vote():
    party = request.form.get("party")
    voter_id = request.form.get("voter_id")

    if not party or not voter_id:
        flash('All fields are required!', 'error')
        return redirect('/')

    if voter_id not in VOTER_IDS:
        flash('Invalid Voter ID. Please use a valid sample ID.', 'error')
        return redirect('/')

    if voter_id in vote_check:
        flash(f'Voter ID {voter_id} has already voted!', 'error')
        return redirect('/')

    vote_check.append(voter_id)

    post_object = {
        'voter_id': voter_id,
        'party': party,
        'timestamp': datetime.datetime.now().timestamp()
    }

    # Send the vote to the blockchain
    new_tx_address = f"{CONNECTED_SERVICE_ADDRESS}/new_transaction"
    requests.post(new_tx_address, json=post_object, headers={'Content-type': 'application/json'})

    flash(f'Vote successfully cast for {party}!', 'success')
    return redirect('/')

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
