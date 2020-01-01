from btcpy.setup import setup
from btcpy.structs.script import P2pkhScript, ScriptSig
from btcpy.structs.sig import IfElseSolver, HashlockSolver, P2pkhSolver, Branch
from btcpy.structs.transaction import TransactionFactory
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
from utils import *

setup('testnet', strict=True)
coin_symbol='btc-testnet'
api_key = 'fe4a832ab7d14936b5731aa79cfa58ae'

# commiter
pubk_hex = '02da815705edf454adf8cbbffe76550478219424c2e95d906708e17cd422297c31'
privk_hex = '83e5bdfd9522d198c068cb2a7be41bf74cec5a3b02d80f26688ba9dfb44cdb52'
pubk = PublicKey.unhexlify(pubk_hex)
privk = PrivateKey.unhexlify(privk_hex)

# 创建输入脚本
secret = 'I have an apple'  # 需要展示的秘密
p2pkh_solver = P2pkhSolver(privk)
hasklock_solver = HashlockSolver(secret.encode(), p2pkh_solver)
if_solver = IfElseSolver(Branch.IF,  # branch selection
                         hasklock_solver)
# 创建输出脚本
script = P2pkhScript(pubk)

# 创建交易
to_spend_hash = "45bb545f43df256fd41e0a6cbd9f63122ea3f3cc200f1aa4a68deff23edfbf0d"
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
                                          script_pubkey=script),
                                    ],
                              locktime=Locktime(0))

signed = unsigned.spend([to_spend.outs[0]], [if_solver])


from blockcypher import pushtx

msg = pushtx(coin_symbol=coin_symbol, api_key=api_key, tx_hex=signed.hexlify())

format_output(msg)
