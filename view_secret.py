from utils import *
from btcpy.setup import setup
from btcpy.structs.transaction import TransactionFactory

# global
setup('testnet', strict=True)
coin_symbol = 'btc-testnet'

# 获取Open交易
open_tx_hash = '61fe8f28851536c3778b90ba58d649751e5b088af26069992fe52faca0239828'  # open交易的hash
raw_open_tx = get_raw_tx(open_tx_hash, coin_symbol)
open_tx = TransactionFactory.unhexlify(raw_open_tx)  # decode raw transaction
open_tx = open_tx.to_json()

# 获取输入脚本
scriptSig = open_tx['vin'][0]['scriptSig']['asm']

# 将输入脚本按空格分割
scriptSig_list = scriptSig.split()

# 如无意外，秘密应该在脚本的倒数第二个位置
secret_hex = scriptSig_list[-2]

# 从hex将秘密解码出来
print('secret hex: ', secret_hex)
print('decoded secret: ', bytes.fromhex(secret_hex).decode())
