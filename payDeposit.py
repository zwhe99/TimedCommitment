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
pubk_hex = '024fa55e08d8fa261fd12060aa1f68357b1f284a93edfd922ddb7910170aa55dae'
privk_hex = 'aa35ddba99229ff38902f4969a2b3c0de4d8be45ad8c3858aeb2c3c6f663fdea'
pubk = PublicKey.unhexlify(pubk_hex)
privk = PrivateKey.unhexlify(privk_hex)

# 输出脚本
script = P2pkhScript(pubk)

to_spend_hash = "9afc5dc0cb3f5c644c134b062f2c608ce37d571e055fcea0eca5285b519ae697"
to_spend_raw = get_raw_tx(to_spend_hash, coin_symbol)
to_spend = TransactionFactory.unhexlify(to_spend_raw)
penalty = int(float(to_spend.to_json()['vout'][0]['value']) * (10**8))

print('estimating mining fee...')
mining_fee_per_kb = get_mining_fee_per_kb(coin_symbol, api_key, condidence='high')
estimated_tx_size = cal_tx_size_in_byte(inputs_num=1, outputs_num=1)
mining_fee = int(mining_fee_per_kb * (estimated_tx_size / 1000)) * 2

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
else_solver = IfElseSolver(Branch.ELSE,
                           RelativeTimelockSolver(Sequence(5), P2pkhSolver(privk)))
signed = unsigned.spend([to_spend.outs[0]], [else_solver])

print('pay_desposit_hex:', signed.hexlify())


msg = boardcast_raw_tx(signed.hexlify())

format_output(msg)
