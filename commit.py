from btcpy.setup import setup
from btcpy.structs.address import P2pkhAddress
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.script import Hashlock256Script
from btcpy.structs.sig import *
from btcpy.structs.transaction import TransactionFactory
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
from utils import *
import hashlib

setup('testnet', strict=True)
coin_symbol = 'btc-testnet'
api_key = 'fe4a832ab7d14936b5731aa79cfa58ae'

# committer
pubk_hex = '02da815705edf454adf8cbbffe76550478219424c2e95d906708e17cd422297c31'
pubk = PublicKey.unhexlify(pubk_hex)
address = P2pkhAddress(pubk.hash())

privk_hex = '83e5bdfd9522d198c068cb2a7be41bf74cec5a3b02d80f26688ba9dfb44cdb52'
privk = PrivateKey.unhexlify(privk_hex)

# recipient
pubk_hex2 = '022ddaf15c9fb39f16ec5f15246bd50379541250f49a38207c8e8c4e50994c0a2e'
pubk2 = PublicKey.unhexlify(pubk_hex2)

# a sample of secret
secret = 'I have an apple'.encode()
secret_hash = hashlib.sha256(hashlib.sha256(secret).digest()).digest()
secret_hash = StackData.from_bytes(secret_hash)

# sequence(lock_time)
sequence = 5

print("秘密经过sha256加密结果:", secret_hash)

# 创建输出脚本
# 定时脚本
lock_time_script = IfElseScript(
    # if branch
    Hashlock256Script(secret_hash,
                      P2pkhScript(pubk)),
    # else branch
    RelativeTimelockScript(  # timelocked script
        Sequence(sequence),  # expiration, 5 blocks
        P2pkhScript(pubk2)
    )
)
print("lock_time_script.type: ", lock_time_script.type)
print("lock_time_script str: ", str(lock_time_script))

# 找零脚本
change_script = P2pkhScript(pubk)

# 开始创建交易
print("sweeping fund...")
to_spend_hash, balance = sweep_fund(privkey=privk_hex, address=str(address), coin_symbol=coin_symbol,
                                    api_key=api_key)
print('estimating mining fee...')
mining_fee_per_kb = get_mining_fee_per_kb(coin_symbol, api_key, condidence='high')
estimated_tx_size = cal_tx_size_in_byte(1, 2)
mining_fee = (mining_fee_per_kb * estimated_tx_size) * 1000

penalty = 100000
assert penalty + mining_fee <= balance, 'commiter账户余额不足'

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
