from blockcypher import simple_spend
from blockcypher import get_address_overview
from blockcypher import get_transaction_details
import json


def format_output(data):
    print(json.dumps(data, sort_keys=False, indent=2))


def sweep_fund(privkey, address, coin_symbol, api_key):
    tx_hash = simple_spend(from_privkey=privkey,
                           to_address=address, to_satoshis=-1, coin_symbol=coin_symbol, api_key=api_key)

    tx = get_transaction_details(tx_hash, coin_symbol=coin_symbol)
    balance = tx['total']
    return tx_hash, balance


def get_balance(address, coin_symbol):
    msg = get_address_overview(address, coin_symbol)
    return msg['balance']


def get_raw_tx(tx_hash, coin_symbol):
    tx = get_transaction_details(tx_hash, coin_symbol, include_hex=True)
    return tx['hex']
