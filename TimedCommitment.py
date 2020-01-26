from btcpy.setup import setup
from btcpy.structs.address import P2pkhAddress
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.script import Hashlock256Script
from btcpy.structs.sig import *
from btcpy.structs.transaction import TransactionFactory, HeightBasedSequence, TimeBasedSequence
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
from utils import *
import hashlib
from blockcypher import pushtx

# global
setup('testnet', strict=True)
coin_symbol = 'btc-testnet'


class User:
    def __init__(self, pubk, privk=None, api_key=None):
        self.api_key = api_key
        if isinstance(pubk, str):
            self.pubk = PublicKey.unhexlify(pubk)
        elif isinstance(pubk, PublicKey):
            self.pubk = pubk
        else:
            raise ValueError('pubk should be str or PublicKey')

        if privk is None:
            self.privk = None
        elif isinstance(privk, str):
            self.privk = PrivateKey.unhexlify(privk)
        elif isinstance(privk, PrivateKey):
            self.privk = privk
        else:
            raise ValueError('privk should be str or PrivateKey')

        self.address = P2pkhAddress(self.pubk.hash())


def commit(committer, receiver, secret, type, lock_time, penalty):
    if type not in ['Timed', 'Height']:
        raise ValueError("type should be 'Timed' or 'Height'")

    secret_hash = hashlib.sha256(hashlib.sha256(secret.encode()).digest()).digest()
    secret_hash = StackData.from_bytes(secret_hash)
    print("秘密经hash256加密结果:", secret_hash)

    # 创建输出脚本
    if type is 'Height':

        # Relative - HeightBased
        sequence = lock_time
        lock_time_script = IfElseScript(
            # if branch
            Hashlock256Script(secret_hash,
                              P2pkhScript(committer.pubk)),
            # else branch
            RelativeTimelockScript(  # timelocked script
                HeightBasedSequence(sequence),  # expiration
                P2pkhScript(receiver.pubk)
            )
        )
    else:
        # Relative - TimedBased
        time_delta = datetime.timedelta(minutes=lock_time)
        time_now = datetime.datetime.now()
        print("current time: ", time_now.strftime("%y-%m-%d %H:%M:%S"))
        print("pay deposit time: ", (time_now + time_delta).strftime("%y-%m-%d %H:%M:%S"))

        lock_time_script = IfElseScript(
            # if branch
            Hashlock256Script(secret_hash,
                              P2pkhScript(committer.pubk)),
            # else branch
            RelativeTimelockScript(  # timelocked script
                TimeBasedSequence.from_timedelta(time_delta),  # expiration
                P2pkhScript(receiver.pubk)
            )
        )

    # 找零脚本
    change_script = P2pkhScript(committer.pubk)

    # 清理资产
    print("sweeping fund...")
    to_spend_hash, balance = sweep_fund(privkey=str(committer.privk), address=str(committer.address),
                                        coin_symbol=coin_symbol,
                                        api_key=committer.api_key)

    # 估算挖矿费用
    print('estimating mining fee...')
    mining_fee_per_kb = get_mining_fee_per_kb(coin_symbol, committer.api_key, condidence='high')
    estimated_tx_size = cal_tx_size_in_byte(inputs_num=1, outputs_num=2)
    mining_fee = int(mining_fee_per_kb * (estimated_tx_size / 1000)) * 2

    # 设置罚金
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
    solver = P2pkhSolver(committer.privk)

    # 修改交易
    signed = unsigned.spend([to_spend.outs[0]], [solver])
    print('commit_tx_hex: ', signed.hexlify())

    # 发送交易
    tx = pushtx(coin_symbol=coin_symbol, api_key=committer.api_key, tx_hex=signed.hexlify())
    format_output(tx)
