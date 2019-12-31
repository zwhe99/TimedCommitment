from btcpy.setup import setup
from btcpy.structs.script import P2pkhScript, ScriptSig
from btcpy.structs.sig import IfElseSolver, HashlockSolver, P2pkhSolver, Branch
from btcpy.structs.transaction import TransactionFactory
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction

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
to_spend = TransactionFactory.unhexlify(
    '0200000001e0bcb851a6cda1a55754c705572b240412404c25f15fe5c1de3df2c0c62a879d000000006a47304402201794924b777483adf954b8b8def930e8c2d7bbf8c7e4fbd3bf8c8af4a402fe7802206c257e320450592d2579695b4808877a08f48b2c768d48541835b7d36cfb6be8012102da815705edf454adf8cbbffe76550478219424c2e95d906708e17cd422297c31ffffffff02a0860100000000005b63aa2059d47d5565ce1e8df0772e5c00abdb31b8ca140017511a8afe6ba567fb27b79d8876a914a34e42492a174ef8fb4f3482d1c07cf19e1181e788ac6755b27576a914c444b5ac9f3a3a26b1f99b57107ebbdf50ca7e7788ac6800350c00000000001976a914a34e42492a174ef8fb4f3482d1c07cf19e1181e788ac00000000')
unsigned = MutableTransaction(version=2,
                              ins=[TxIn(txid=to_spend.txid,
                                        txout=0,
                                        script_sig=ScriptSig.empty(),
                                        sequence=Sequence.max())],
                              outs=[TxOut(value=80000,
                                          n=0,
                                          script_pubkey=script),
                                    ],
                              locktime=Locktime(0))

signed = unsigned.spend([to_spend.outs[0]], [if_solver])


from blockcypher import pushtx

msg = pushtx(coin_symbol=coin_symbol, api_key=api_key, tx_hex=signed.hexlify())

print(msg)
