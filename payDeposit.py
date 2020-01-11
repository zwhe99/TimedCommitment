from btcpy.setup import setup
from btcpy.structs.script import P2pkhScript, ScriptSig
from btcpy.structs.sig import IfElseSolver, P2pkhSolver, Branch, RelativeTimelockSolver
from btcpy.structs.transaction import TransactionFactory, TimeBasedSequence, HeightBasedSequence
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
from utils import *
import datetime

# global
setup('testnet', strict=True)
coin_symbol = 'btc-testnet'
api_key = 'fe4a832ab7d14936b5731aa79cfa58ae'

# recipient
pubk_hex = '03fb2cd4d0b5248c5f62296e55ce59eab79d68b90fc1d9865bafbcaa556e1c766c'
privk_hex = '56cc7c6c7b44896b7dcdece50de8a9801024f6d9718d172a64f2be30aa128ff0'
pubk = PublicKey.unhexlify(pubk_hex)
privk = PrivateKey.unhexlify(privk_hex)

# 获取 commit 交易
to_spend_hash = "bd7fcee69cfeb188d97befcd4d591359a6d0797d2811adee1c7fc76482d09787"
to_spend_raw = get_raw_tx(to_spend_hash, coin_symbol)
to_spend = TransactionFactory.unhexlify(to_spend_raw)

# 获取罚金数额
penalty = int(float(to_spend.to_json()['vout'][0]['value']) * (10 ** 8))

# 输出脚本
script = P2pkhScript(pubk)

# 计算挖矿费用
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
                                          script_pubkey=script)],
                              locktime=Locktime(0))

# 输入脚本

# Relative - HeightBased
else_solver = IfElseSolver(Branch.ELSE,  # Branch selection
                           RelativeTimelockSolver(HeightBasedSequence(0x00000002),
                                                  P2pkhSolver(privk)))

# Relative - TimeBased
# else_solver = IfElseSolver(Branch.ELSE,  # Branch selection
#                            RelativeTimelockSolver(TimeBasedSequence.from_timedelta(datetime.timedelta(minutes=5)),
#                                                   P2pkhSolver(privk)))

# 修改交易
signed = unsigned.spend([to_spend.outs[0]], [else_solver])

# 广播交易
print('pay_desposit_hex:', signed.hexlify())
msg = broadcast_raw_tx(signed.hexlify())
format_output(msg)
