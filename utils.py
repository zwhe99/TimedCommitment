from blockcypher import simple_spend
from blockcypher import get_address_overview
from blockcypher import get_transaction_details
from blockcypher import get_blockchain_overview
import json


def format_output(data):
    print(json.dumps(data, sort_keys=False, indent=2))


def get_mining_fee_per_kb(coin_symbol, api_key, condidence):
    assert condidence in {'high', 'medium', 'low'}, str(condidence) + "isn't in {'high','medium','low'} "

    bc = get_blockchain_overview(coin_symbol, api_key)
    if condidence == 'high':
        return bc['high_fee_per_kb']

    elif condidence == 'medium':
        return bc['medium_fee_per_kb']

    elif condidence == 'low':
        return bc['low_fee_per_kb']


def cal_tx_size_in_byte(inputs_num, outputs_num):
    return inputs_num * 180 + outputs_num * 34 + 10


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


print(get_mining_fee_per_kb('btc-testnet', 'fe4a832ab7d14936b5731aa79cfa58ae', 'low'))
