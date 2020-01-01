from btcpy.setup import setup
from btcpy.structs.script import P2pkhScript, ScriptSig
from btcpy.structs.sig import IfElseSolver, P2pkhSolver, Branch, RelativeTimelockSolver
from btcpy.structs.transaction import TransactionFactory
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
from utils import *

setup('testnet', strict=True)
coin_symbol='btc-testnet'
api_key = 'fe4a832ab7d14936b5731aa79cfa58ae'

# recipient
pubk_hex = '022ddaf15c9fb39f16ec5f15246bd50379541250f49a38207c8e8c4e50994c0a2e'
privk_hex = '829af0cb61493f449f888ce4a3d2df48b98e81a49a825f2627744245b9fd89e3'
pubk = PublicKey.unhexlify(pubk_hex)
privk = PrivateKey.unhexlify(privk_hex)

# 输出脚本
script = P2pkhScript(pubk)

to_spend_hash = "dae543cdd17e08908881cdcc1281e854576ed0dff3cdc835dfc1eb188628fbf8"
to_spend_raw = get_raw_tx(to_spend_hash, coin_symbol)
to_spend = TransactionFactory.unhexlify(to_spend_raw)
penalty = int(float(to_spend.to_json()['vout'][0]['value']) * (10**8))

unsigned = MutableTransaction(version=2,
                              ins=[TxIn(txid=to_spend.txid,
                                        txout=0,
                                        script_sig=ScriptSig.empty(),
                                        sequence=Sequence.max())],
                              outs=[TxOut(value=penalty,
                                          n=0,
                                          script_pubkey=script)],
                              locktime=Locktime(0))

# 输入脚本
else_solver = IfElseSolver(Branch.ELSE,
                           RelativeTimelockSolver(Sequence(5), P2pkhSolver(privk)))
signed = unsigned.spend([to_spend.outs[0]], [else_solver])

from blockcypher import pushtx

msg = pushtx(coin_symbol=coin_symbol, api_key=api_key, tx_hex=signed.hexlify())

print(msg)
