from btcpy.setup import setup
from btcpy.structs.address import P2pkhAddress
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.script import Hashlock256Script
from btcpy.structs.sig import *
from btcpy.structs.transaction import TransactionFactory, HeightBasedSequence, TimeBasedSequence
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
from utils import *
import hashlib
import datetime

# global
setup('testnet', strict=True)
coin_symbol = 'btc-testnet'
api_key = 'fe4a832ab7d14936b5731aa79cfa58ae'

# committer
pubk_hex = '0380557a219119218f7830bf3cdb2bb3c8220cac15db97e255498fb992e68c04a9'
pubk = PublicKey.unhexlify(pubk_hex)
address = P2pkhAddress(pubk.hash())

privk_hex = '385acd25450e50ecd5ad0fffec7b871c8f75eb3ba9ecded8d35a0765f4763d7e'
privk = PrivateKey.unhexlify(privk_hex)

# recipient
pubk_hex2 = '03fb2cd4d0b5248c5f62296e55ce59eab79d68b90fc1d9865bafbcaa556e1c766c'
pubk2 = PublicKey.unhexlify(pubk_hex2)

# a sample of secret
secret = 'I have an apple'.encode()
secret_hash = hashlib.sha256(hashlib.sha256(secret).digest()).digest()
secret_hash = StackData.from_bytes(secret_hash)
print("秘密经hash256加密结果:", secret_hash)

# 创建输出脚本

# 定时脚本

# Relative - HeightBased
sequence = 0x00000002
lock_time_script = IfElseScript(
    # if branch
    Hashlock256Script(secret_hash,
                      P2pkhScript(pubk)),
    # else branch
    RelativeTimelockScript(  # timelocked script
        HeightBasedSequence(sequence),  # expiration, 5 blocks
        P2pkhScript(pubk2)
    )
)

# Relative - TimedBased
# time_delta = datetime.timedelta(minutes=5)
# time_now = datetime.datetime.now()
# print("current time: ", time_now.strftime("%y-%m-%d %H:%M:%S"))
# print("pay deposit time: ", (time_now + time_delta).strftime("%y-%m-%d %H:%M:%S"))
#
# lock_time_script = IfElseScript(
#     # if branch
#     Hashlock256Script(secret_hash,
#                       P2pkhScript(pubk)),
#     # else branch
#     RelativeTimelockScript(  # timelocked script
#         TimeBasedSequence.from_timedelta(time_delta),  # expiration, 5 blocks
#         P2pkhScript(pubk2)
#     )
# )

print("lock_time_script.type: ", lock_time_script.type)
print("lock_time_script str: ", str(lock_time_script))

# 找零脚本
change_script = P2pkhScript(pubk)

# 清理资产
print("sweeping fund...")
to_spend_hash, balance = sweep_fund(privkey=privk_hex, address=str(address), coin_symbol=coin_symbol,
                                    api_key=api_key)

# 估算挖矿费用
print('estimating mining fee...')
mining_fee_per_kb = get_mining_fee_per_kb(coin_symbol, api_key, condidence='high')
estimated_tx_size = cal_tx_size_in_byte(inputs_num=1, outputs_num=2)
mining_fee = int(mining_fee_per_kb * (estimated_tx_size / 1000)) * 2

# 设置罚金
penalty = 100000
assert penalty + mining_fee <= balance, 'committer账户余额不足'

# 创建交易
to_spend_raw = get_raw_tx(to_spend_hash, coin_symbol)
to_spend = TransactionFactory.unhexlify(to_spend_raw)

unsigned = MutableTransaction(version=2,
                              ins=[TxIn(txid=to_spend.txid,
                                        txout=0,
                                        script_sig=ScriptSig.empty(),
                                        sequence=Sequence.max())],
                              outs=[TxOut(value=penalty,
                                          n=0,
                                          script_pubkey=lock_time_script),
                                    TxOut(value=balance - penalty - mining_fee,
                                          n=1,
                                          script_pubkey=change_script)],
                              locktime=Locktime(0))
# 输入脚本
solver = P2pkhSolver(privk)

# 修改交易
signed = unsigned.spend([to_spend.outs[0]], [solver])
print('commit_tx_hex: ', signed.hexlify())

# 发送交易
from blockcypher import pushtx

tx = pushtx(coin_symbol=coin_symbol, api_key=api_key, tx_hex=signed.hexlify())
format_output(tx)
