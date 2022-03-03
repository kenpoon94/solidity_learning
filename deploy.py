from solcx import compile_standard, install_solc
from web3 import Web3
from dotenv import load_dotenv
import json, os

load_dotenv()
install_solc("0.6.0")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile solidity
compile_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "SimpleStorage.sol": {
                "content": simple_storage_file,
            }
        },
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

# Dump into .json
with open("compiled_code.json", "w") as file:
    json.dump(compile_sol, file)


# Get bytecode
bytecode = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Get abi
abi = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


# Ganache variables
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = os.getenv("PRIVATE_KEY")

# Create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get latest tx
nonce = w3.eth.getTransactionCount(address)

################################################################################
# Build tx
print("Deploying contract...")
transaction = SimpleStorage.constructor().buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": address, "nonce": nonce}
)

# Sign tx
signed_tx = w3.eth.account.sign_transaction(transaction, private_key)

# Send tx
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

# Wait for tx
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contract deployed successfully")

################################################################################
# Work with contract
print("Creating transaction...")
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulte making the call and getting a return value (no state change)
# Transact -> Actually make a state change
# print(simple_storage.functions.retrieve().call())

# Create store tx
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": address,
        "nonce": nonce + 1,
    }
)
signed_store_tx = w3.eth.account.sign_transaction(store_transaction, private_key)

store_tx_hash = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)

store_tx_receipt = w3.eth.wait_for_transaction_receipt(store_tx_hash)
print("Transaction processed successfully")

print(simple_storage.functions.retrieve().call())
