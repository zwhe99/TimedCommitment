from TimedCommitment import User, commit_tx, open_tx, get_secret
import time
pubk_hex = '0380557a219119218f7830bf3cdb2bb3c8220cac15db97e255498fb992e68c04a9'
privk_hex = '385acd25450e50ecd5ad0fffec7b871c8f75eb3ba9ecded8d35a0765f4763d7e'
api_key = 'fe4a832ab7d14936b5731aa79cfa58ae'

pubk_hex2 = '03fb2cd4d0b5248c5f62296e55ce59eab79d68b90fc1d9865bafbcaa556e1c766c'
privk_hex2 = '56cc7c6c7b44896b7dcdece50de8a9801024f6d9718d172a64f2be30aa128ff0'

committer = User(pubk_hex, privk_hex, api_key=api_key)
receiver = User(pubk_hex2)

with open("secret.txt", "r") as f:  # 打开文件
    secret = f.read()  # 读取文件
    print(type(secret))

commit_tx_hash = commit_tx(committer, receiver, secret=secret, type='Timed', lock_time=5, penalty=10000)

time.sleep(5)

open_tx_hash = open_tx(committer, secret, commit_tx_hash)

time.sleep(5)

get_secret(open_tx_hash)
