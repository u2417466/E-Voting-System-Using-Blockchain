# **1. Introduction**
## **1.1 Overview**
The Blockchain-Based E-Voting System provides users a secure transparent digital voting platform which utilizes blockchain technology for tamper-proof recording of votes. The system resolves major electronic voting obstacles related to fraud prevention together with anonymity and verifiability.
## **1.2 Objectives**
- Develop a decentralized, immutable voting ledger.
- Ensure that each voter can cast only one vote.
- Provide real-time voting results while maintaining voter privacy.
- Enable secure blockchain-based data storage.

# **2. System Architecture**
## **2.1 Components**
The system consists of three main components:

- **Blockchain Network (Backend)** 
  - Stores votes as transactions on the blockchain.
  - Implements Proof-of-Work (PoW) to validate transactions.
  - Ensures data integrity and prevents tampering.
- **Flask Web Application (Frontend)** 
  - Provides a user-friendly voting interface.
  - Allows voters to submit votes securely.
  - Displays real-time voting results.
- **Database (Blockchain Ledger)** 
  - Stores blocks containing votes.
  - Ensures each voter ID is unique.
## **2.2 System Flow**
1. A voter selects a political party and enters their unique Voter ID.
1. The vote is submitted as a transaction to the blockchain.
1. The system mines a new block to confirm the vote.
1. The blockchain updates, and results are displayed in real-time.

# **3. Implementation**
## **3.1 Technologies Used**

|**Technology**|**Purpose**|
| - | - |
|Flask|Web framework for the voting interface|
|Python|Backend programming language|
|Blockchain (PoW)|Secure vote storage mechanism|
|HTML/CSS/JS|Frontend design for user interaction|
|Requests Library|API communication between frontend and blockchain|
## **3.2 Project Structure**
- app
  - \_\_init\_\_.py
  - views.py
- blockchain
  - service.py	
- templates
  - base.html
  - index.html
- app.py
- config.py
- README.md
- requirements.txt
# **4. Installation Guide**
## **4.1 Prerequisites**
- Install Python 3.x
- Install pip (Python package manager)
## **4.2 Installation Steps**
**Clone the repository:**

git clone https://github.com/u2417466/E-Voting-System-Using-Blockchain.git

cd E-Voting-System-Using-Blockchain

**Install dependencies:**

pip install -r requirements.txt

**Run the Blockchain Service:**

python blockchain/service.py

This starts the blockchain at http://127.0.0.1:8000

**Run the Web Application:**

python app.py

The voting UI will be available at http://127.0.0.1:5000
# **5. Features & Functionality**
## **5.1 Blockchain Security**
- Each vote is hashed and stored in an immutable ledger.
- Uses Proof-of-Work (PoW) to verify transactions.
- Only valid votes are accepted.
## **5.2 Web Interface**
- User-friendly voting page (index.html).
- Real-time vote updates.
- Resync, Mine, and View Blockchain options.
## **5.3 APIs**

|**Endpoint**|**Function**|
| - | - |
|/new\_transaction|Submits a new vote transaction|
|/chain|Retrieves the blockchain data|
|/mine|Mines pending transactions|
|/register\_node|Registers a new node|
# **6 Testing & Validation**
## **6.1 Testing Plan**

|**Test Case**|**Expected Result**|
| - | - |
|Submit vote with valid Voter ID|Vote recorded successfully|
|Submit vote with duplicate Voter ID|Error: "Voter has already voted"|
|View blockchain data|Displays all recorded votes|
|Mine transactions|Confirms and adds votes to the blockchain|
##
## **6.2 Test Execution**
- Unit Tests for blockchain validation.
- Manual Testing for UI interaction.
# **7. Conclusion & Future Enhancements**
## **7.1 Conclusion**
The Blockchain-Based E-Voting System exhibits secure transparent and everlasting voting records through blockchain technology. Through the system voters obtain fair elections and its anti-fraud capabilities enable immediate results.
## **7.2 Future Enhancements**
- Smart Contract Implementation for automated validation.
- Decentralized Nodes for greater security.
- Mobile Application Support for wider accessibility.
# **8. References**
1. Nakamoto, S. (2008). *Bitcoin: A Peer-to-Peer Electronic Cash System*.
1. Wood, G. (2014). *Ethereum: A Secure Decentralized Generalized Transaction Ledger*.
1. GeeksForGeeks. (2023). *Blockchain-Based Voting Systems*.

