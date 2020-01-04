from btcpy.setup import setup
from btcpy.structs.script import P2pkhScript, ScriptSig
from btcpy.structs.sig import IfElseSolver, HashlockSolver, P2pkhSolver, Branch
from btcpy.structs.transaction import TransactionFactory
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
from utils import *

# global
setup('testnet', strict=True)
coin_symbol = 'btc-testnet'
api_key = 'fe4a832ab7d14936b5731aa79cfa58ae'

# committer
pubk_hex = '03acb78908123c649e65d5e3689c3c53c25725c6eb53a6aa7834f73127c4eb2db1'
privk_hex = '24ee94da001fd72ff33b315659f808a3bcd963499086798b634c83258383891f'
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

# 获取commit交易
to_spend_hash = "59ceb0cd9cb8a63ff8cc3a4c6979dcb29b2af81b267829035a5ac3d409c85e98"
to_spend_raw = get_raw_tx(to_spend_hash, coin_symbol)
to_spend = TransactionFactory.unhexlify(to_spend_raw)

# 获取罚金数额
penalty = int(float(to_spend.to_json()['vout'][0]['value']) * (10 ** 8))

# 估算挖矿费用
print('estimating mining fee...')
mining_fee_per_kb = get_mining_fee_per_kb(coin_symbol, api_key, condidence='high')
estimated_tx_size = cal_tx_size_in_byte(inputs_num=1, outputs_num=1)
mining_fee = int(mining_fee_per_kb * (estimated_tx_size / 1000)) * 2

# 创建交易
unsigned = MutableTransaction(version=2,
                              ins=[TxIn(txid=to_spend.txid,
                                        txout=0,
                                        script_sig=ScriptSig.empty(),
                                        sequence=Sequence.max())],
                              outs=[TxOut(value=penalty - mining_fee,
                                          n=0,
                                          script_pubkey=script),
                                    ],
                              locktime=Locktime(0))

# 修改交易
signed = unsigned.spend([to_spend.outs[0]], [if_solver])

# 广播交易
print('open_tx_hex: ', signed.hexlify())

from blockcypher import pushtx

msg = pushtx(coin_symbol=coin_symbol, api_key=api_key, tx_hex=signed.hexlify())
format_output(msg)
