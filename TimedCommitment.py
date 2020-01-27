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


def commit_tx(committer, receiver, secret, type, lock_time, penalty):
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
    return tx['tx']['hash']


def open_tx(committer, secret, commit_tx_hash):
    # 创建输入脚本
    p2pkh_solver = P2pkhSolver(committer.privk)
    hasklock_solver = HashlockSolver(secret.encode(), p2pkh_solver)
    if_solver = IfElseSolver(Branch.IF,  # branch selection
                             hasklock_solver)
    # 创建输出脚本
    script = P2pkhScript(committer.pubk)

    # 获取commit交易
    to_spend_raw = get_raw_tx(commit_tx_hash, coin_symbol)
    to_spend = TransactionFactory.unhexlify(to_spend_raw)

    # 获取罚金数额
    penalty = int(float(to_spend.to_json()['vout'][0]['value']) * (10 ** 8))

    # 估算挖矿费用
    print('estimating mining fee...')
    mining_fee_per_kb = get_mining_fee_per_kb(coin_symbol, committer.api_key, condidence='high')
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
    msg = pushtx(coin_symbol=coin_symbol, api_key=committer.api_key, tx_hex=signed.hexlify())
    format_output(msg)

    return msg['tx']['hash']


def get_secret(open_tx_hash):
    # 获取Open交易
    raw_open_tx = get_raw_tx(open_tx_hash, coin_symbol)
    open_tx_raw = TransactionFactory.unhexlify(raw_open_tx)  # decode raw transaction
    open_tx_json = open_tx_raw.to_json()

    # 获取输入脚本
    scriptSig = open_tx_json['vin'][0]['scriptSig']['asm']

    # 将输入脚本按空格分割
    scriptSig_list = scriptSig.split()

    # 如无意外，秘密应该在脚本的倒数第二个位置
    secret_hex = scriptSig_list[-2]

    # 从hex将秘密解码出来
    print('secret hex: ', secret_hex)
    print('decoded secret: ', bytes.fromhex(secret_hex).decode())
