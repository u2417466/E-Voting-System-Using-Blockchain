import datetime  # Importing the datetime module for handling date and time
import json  # Importing JSON for data serialization
import requests  # Importing requests for making HTTP requests
from flask import render_template, redirect, request, flash  # Importing necessary functions from Flask
from app import app  # Importing the Flask app instance
from config import Config  # Importing configuration settings

# The node with which our application interacts (Blockchain Service)
CONNECTED_SERVICE_ADDRESS = Config.BLOCKCHAIN_URL  # URL of the blockchain service
POLITICAL_PARTIES = ["Democratic Party", "Republican Party", "Socialist Party"]  # List of political parties
VOTER_IDS = [  # List of valid voter IDs
    'VOID001', 'VOID002', 'VOID003',
    'VOID004', 'VOID005', 'VOID006',
    'VOID007', 'VOID008', 'VOID009',
    'VOID010', 'VOID011', 'VOID012',
    'VOID013', 'VOID014', 'VOID015'
]

vote_check = []  # List to keep track of voters who have already voted
posts = []  # List to hold the fetched posts from the blockchain

def fetch_posts():
    """
    Fetch the blockchain chain data and parse it for display.
    """
    get_chain_address = f"{CONNECTED_SERVICE_ADDRESS}/chain"  # Construct the URL to get the blockchain data
    response = requests.get(get_chain_address)  # Make a GET request to fetch the chain data

    if response.status_code == 200:  # Check if the request was successful
        content = []  # Initialize a list to hold transaction data
        chain = json.loads(response.content)  # Parse the JSON response
        for block in chain["chain"]:  # Iterate through each block in the chain
            for tx in block["transactions"]:  # Iterate through each transaction in the block
                tx["index"] = block["index"]  # Add the block index to the transaction
                tx["hash"] = block["previous_hash"]  # Add the previous block's hash to the transaction
                content.append(tx)  # Append the transaction to the content list

        global posts  # Declare posts as a global variable
        posts = sorted(content, key=lambda k: k['timestamp'], reverse=True)  # Sort transactions by timestamp in descending order

@app.route('/')  # Define the route for the index page
def index():
    fetch_posts()  # Fetch posts from the blockchain

    # Prepare vote summary
    vote_summary = {}  # Initialize a dictionary to hold the vote summary
    for post in posts:  # Iterate through each post
        party = post["party"]  # Get the party from the post
        if party in vote_summary:  # Check if the party is already in the summary
            vote_summary[party] += 1  # Increment the vote count for the party
        else:
            vote_summary[party] = 1  # Initialize the vote count for the party

    return render_template(  # Render the index template with the necessary data
        'index.html',
        title='E-Voting System Using Blockchain',  # Title for the page
        posts=posts,  # Pass the posts to the template
        vote_summary=vote_summary,  # Pass the vote summary to the template
        readable_time=timestamp_to_string,  # Pass the function to convert timestamps to strings
        political_parties=POLITICAL_PARTIES,  # Pass the list of political parties to the template
        voter_ids=VOTER_IDS  # Pass the list of voter IDs to the template
    )

@app.route('/submit', methods=['POST'])  # Define the route for submitting votes
def submit_vote():
    party = request.form.get("party")  # Get the selected party from the form
    voter_id = request.form.get("voter_id")  # Get the voter ID from the form

    if not party or not voter_id:  # Check if both fields are filled
        flash('All fields are required!', 'error')  # Flash an error message
        return redirect('/')  # Redirect back to the index page

    if voter_id not in VOTER_IDS:  # Check if the voter ID is valid
        flash('Invalid Voter ID. Please use a valid sample ID.', 'error')  # Flash an error message
        return redirect('/')  # Redirect back to the index page

    if voter_id in vote_check:  # Check if the voter has already voted
        flash(f'Voter ID {voter_id} has already voted!', 'error')  # Flash an error message
        return redirect('/')  # Redirect back to the index page

    vote_check.append(voter_id)  # Add the voter ID to the list of voters who have voted

    post_object = {  # Create a dictionary to hold the vote data
        'voter_id': voter_id,  # Add the voter ID
        'party': party,  # Add the selected party
        'timestamp': datetime.datetime.now().timestamp()  # Add the current timestamp
    }

    # Send the vote to the blockchain
    new_tx_address = f"{CONNECTED_SERVICE_ADDRESS}/new_transaction"  # Construct the URL to submit the new transaction
    requests.post(new_tx_address, json=post_object, headers={'Content-type': 'application/json'})  # Make a POST request to submit the vote

    flash(f'Vote successfully cast for {party}!', 'success')  # Flash a success message
    return redirect('/')  # Redirect back to the index page

def timestamp_to_string(epoch_time):  # Function to convert epoch time to a readable string
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')  # Return the formatted date and time
