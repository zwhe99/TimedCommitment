from btcpy.setup import setup
from btcpy.structs.script import P2pkhScript, ScriptSig, StackData
from btcpy.structs.sig import IfElseSolver, P2pkhSolver, Branch, Solver, RelativeTimelockSolver
from btcpy.structs.transaction import TransactionFactory
from btcpy.structs.crypto import PublicKey, PrivateKey
from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction, Sighash

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

to_spend = TransactionFactory.unhexlify(
    '02000000017c6fa51e352bf36709f71677a3da3d0c8849e60e1e1fc3084034fb6246cd2fb1000000006b483045022100c1d8516c7812bedfa8aa6342deac6f0794872d514df02578a5c919d0ca3cf24102200b3f376e7616c66d7d68a00b410941669a6b62b29cf07ab6424edbe001d3fd6f012102da815705edf454adf8cbbffe76550478219424c2e95d906708e17cd422297c31ffffffff02a0860100000000005b63aa2059d47d5565ce1e8df0772e5c00abdb31b8ca140017511a8afe6ba567fb27b79d8876a914a34e42492a174ef8fb4f3482d1c07cf19e1181e788ac6755b27576a914c444b5ac9f3a3a26b1f99b57107ebbdf50ca7e7788ac6800350c00000000001976a914a34e42492a174ef8fb4f3482d1c07cf19e1181e788ac00000000')
unsigned = MutableTransaction(version=2,
                              ins=[TxIn(txid=to_spend.txid,
                                        txout=0,
                                        script_sig=ScriptSig.empty(),
                                        sequence=Sequence.max())],
                              outs=[TxOut(value=10000,
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
