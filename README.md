# Timed Commitment
The implementation of bitcoin-based timed-commitment scheme from "Secure Multiparty Computations on Bitcoin"


教程：定时承诺的实现
==============

定时承诺介绍
----------------

承诺过程包括两个阶段：承诺阶段和开启阶段。通常来说，承诺在两方之间执行：承诺方C和接受方。更一般地说，我们可以假设有n个接受者，表示为$P_1, ...,P_n$. 

* 承诺阶段

  承诺方以某种秘密值$x$启动承诺阶段，即承诺方向接收方传递信息“我拥有秘密$x$”。此值将在开启阶段执行后为每个接受者所知。如果承诺者是诚实的，那么在开始阶段开始之前，对手(接收方)不应该有任何关于$x$的信息

* 开启阶段

  承诺方公开秘密$x$，完成承诺。每个诚实的接受者都可以确信，无论恶意承诺者的行为如何，承诺都可以以一种方式公开，即承诺者既不能反悔也不能使用$x^{'}=x$开启承诺。

* 问题

  没有办法强迫承诺者公开他的秘密$x$。

* 解决方法

  比特币为解决这一问题提供了一种有吸引力的方法。也就是说：使用比特币系统，可以迫使承诺人用一些钱来支持他的承诺，称为押金。如果他在一段时间 $t$ 内拒绝公开承诺，押金将给予其他各方。

  * 首先，假设在协议启动之前，分类账包含n个未赎回的标准交易$U_{1}^{C}、...、U_{n}^{C}$，这些事务可以用一个仅为C已知的私钥进行赎回，且每笔交易具有 d BTC。

  * 该协议被表示为CS(C，$d$，$t$，$s$），它包括两个阶段：承诺阶段CS.Commit（C，$d$，$t$，$s$）（其中$s$包含C提交的消息和一些随机值）和开启阶段CS.Open（C，$d$，$t$，$s$）。

  * 诚实的承诺者总是在时间 $t$ 内开启他的承诺。在这种情况下，承诺方收回押金，即分布式账本中包括可以使用C的密钥赎回的标准交易，且总价值为 （$d * n$）BTC.

  * 此外，如果 C 未在时间 $t$ 之前打开承诺，则每一方都会赚取 d BTC。更确切地说：对于每一个诚实的$P_i$，账本中都包含一个交易，其值为d BTC，可以用$P_i$已知的密钥进行赎回。

    

* 实现一
  
  * 假设$x \in \{0, 1\}^{*}$, 在承诺阶段 C 计算 $s := (x||r)$, 其中 $r$ 是从$\{0, 1\}^{k}$中随机选择的随机数，然后 C 将 $h = H(s)$发送给每一位接收方(这基本上构成他对 $x$ 的“承诺”）。
  
  * 在开启阶段，C 将 $s$发送给每个接收方，接收方检查是否$h=H(s)$，并通过从$s$中剥离最后$k$位来恢复$x$。如果$H(s) \not= h$，接受者将不接受开启过程。
  
  * 协议的基本思想如下
  
    * 承诺方独立地与每个接收者$P_i$交谈。对于每个$P_{i}$，C 将在承诺阶段创建一个价值 d BTC 的交易 $Commit_{i}$. 这笔交易通常被 C 在开启阶段通过交易 $Open_{i}$ 赎回。交易 $Commit_{i}$ 将以 $Open_{i}$ 交易必须自动开启承诺(公布$s$)的方式构建。技术上，可以通过构造 $Commit_{i}$ 的输出脚本来完成，这样 $Open_{i}$就必须提供$s$.
  
    * 这意味着直到 C 揭示$s$前， 他的钱是“冻结”的。
  
    * 然而，为了限制接收方的等待时间，我们还要求 C 向 $P_{i}$ 发送一个交易 $PayDeposit_{i}$ ,使得 $P_{i}$ 可以在时间 $t$ 之后赎回交易 $Commit_{i}$ 。
  
    * 具体的实施过程如图：
  
      ![a8ea7cd1861db26ac5c2b4d4cdb1cf02_1_2_art](img\a8ea7cd1861db26ac5c2b4d4cdb1cf02_1_2_art.png)
      
    	* 关键点在于 $PayDeposit_{i}$ 交易的 **tlock**属性 。由于 **tlock**属性 的存在，$PayDeposit_{i}$ 在时间 $t$之前无法上链。值得注意的是， $PayDeposit_{i}$ 由承诺方构造，并且是需要承诺方 C 和接收方 $P_{i}$ 共同签名的多方签名交易。也就是说，由承诺方设定 **tlock** = $t$ 的条件，并且他自己签名表示同意。待时间满足 **tlock**属性的条件后，接收方 $P_{i}$ 签名，并广播 $PayDeposit_{i}$ 即可获得押金。
    	
    	  
  
* 实现二

  * 事实上由于比特币版本的更新，可以比实现一更简单地实现定时承诺。
  * 实现一将“定时”放在 $PayDeposit_{i}$ 以阻止其在制定时间之前被矿工挖掘。
  * 通过比特币脚本的 OP_CHECKSEQUENCEVERIFY 操作和交易输入的 nSequence 属性，我们可以将“定时”放在  $Commit_{i}$ 的输出脚本中实现。如此一来避免了多方签名和链下传输交易，因为承诺方本来就要对 $Commit_{i}$ 进行签名的。

  * 实现方法

    *  $Open_{i}$ 交易与实现一完全一致
    
    * $Commit_{i}$ 交易的输出脚本更改为：
      $out$-$script(body,\sigma_1,\boldsymbol{x},nSequence):$
      	$(H(\boldsymbol{x}) = h \bigwedge ver_{ \widetilde{C}}(body,\sigma_1))\bigvee(   t<nSequence \bigwedge ver_{ \widetilde{P}}(body,\sigma_2))$
      
      其中：$t$为创建输出脚本时设置的时间锁 ; $t < nSequnce$通过OP_CHECKSEQUENCEVERIFY来实现
      
      写成更简明的形式：
    
      ```
      out-script:
          if{ 
              [hashlock] 
              p2pkh 
          }
          else{ 
              [relativetimelock] 
              p2pkh 
          }
      ```
      
    * $PayDeposit_{i}$ 交易的输入脚本更改为：
    
      $in$-$script$:
      	$nSequence, sig_{\widetilde{P}}([PayDeposit])$
      
    * 更详细的内容请参考《两种定时承诺实现方法的比较》
    
    * 由于本人表达能力有限，如果有模糊的地方请以原始资料为准
    
      *  [BIP68中关于Sequence的定义](https://github.com/bitcoin/bips/blob/master/bip-0068.mediawiki)
      *  [BIP112中关于CHECKSEQUENCEVERIFY的定义](https://github.com/bitcoin/bips/blob/master/bip-0068.mediawiki)
      *  [比特币脚本大全](https://en.bitcoin.it/wiki/Script)
      *  [btcpy文档](https://github.com/chainside/btcpy#scripts)(在网页中搜索"Timelocks, Hashlocks, IfElse"关键词)
    
      
## 环境准备

* **建议全程科学上网**

    * 如果代码运行中出现超时等错误，请检查自己的网络状况

* Ubuntu 18.04.3 LTS

  * blockcypher 对Windows的支持不好，推荐使用Ubuntu系统。

* python 3.7.4

* blockcypher

  * 安装
  	*  ```
    	pip install blockcypher
    	```
    	
    * 请到 https://www.blockcypher.com/ 注册一个账号。注册成功后可以获得一个 Token，这将在执行POST或者DELETE类操作中被使用。
    
      
    
  * 简介

    * BlockCypher是一个简单高效的，用于与区块链进行交互的API。可以通过[api.blockcypher.com](https://api.blockcypher.com/v1/btc/main)，使用HTTP或HTTPS访问。
    
    * 对于普通的请求 BlockCypher 会将频率限制在最高 3 requests/sec 以及 200 requests/hr，请不要短时间内发送过多请求。如果需要解除限制，需要付费。
    
    * BlockCypher具有以下语言的客户端SDK：
      - **Ruby** https://github.com/blockcypher/ruby-client
      
      - **Python** https://github.com/blockcypher/blockcypher-python
      
      - **Java** https://github.com/blockcypher/java-client
      
      - **PHP** https://github.com/blockcypher/php-client
      
      - **Go** https://github.com/blockcypher/gobcy
      
      - **Node.js** https://github.com/blockcypher/node-client
      
        
      
    * 文档链接
      
      * https://www.blockcypher.com/dev/bitcoin/?python#introduction
      
        
      
    * 我们主要使用 blockcypher 完成：地址的生成、交易的广播、钱包信息查询、交易信息查询、区块链信息查询。
    
      

* chainside-btcpy

  * 安装
  
    ```
    pip install ecdsa
    pip install base58
    pip install chainside-btcpy
    ```
    
    
    
  * 简介
    
    * btcpy是一个Python>=3.3 segwiti兼容的库，它提供了以简单的方式处理比特币数据结构的工具。这个库的主要目标是提供一个简单的接口来解析和创建复杂的比特币脚本。
    * **注意: ** 这个库是一个正在开发的库，所以不建议在生产环境中使用它**（但是也找不到别的更好的库了）**。此外，只要版本是0.*， 就要注意 API 有可能产生大的变化。
    * btcpy 的文档不是很全，必要时需要查看其源码。源码中的注释可以帮你更好地理解它的功能。
    * 文档连接
      
      * https://github.com/chainside/btcpy#installation
    * btcpy 是完全离线工作的，不需要访问区块链。我们主要使用 btcpy 完成：脚本和交易的创建、交易的广播
    
    
    
  * **设定**
  
    **首次导入此程序包时要做的第一件事是设置一个全局状态，该状态指示你正在哪个网络上工作以及是否要启用严格模式。**我们将在比特币测试网进行工作，因此设置参数为 'testnet'（**下文不再提示**）。
    
    ```python
    from btcpy.setup import setup
    setup('testnet', strict=True)
    ```
    
    
  
 * 工具类网站
   
    * blockchain exploration
      * https://tbtc.bitaps.com/
      
      * https://live.blockcypher.com/
    
      * 使用上面两个网站查询，有时会出现不一致的情况。一般来说，以第一个网站显示的为准。具体说明请见[广播交易第四点](#广播交易)
      
          
      
    * 手动广播交易
    
      * https://tbtc.bitaps.com/broadcast

        
    
    * 获取比特币测试网测试币
      * https://testnet-faucet.mempool.co/
      
      * https://coinfaucet.eu/en/btc-testnet/
      
      * https://bitcoinfaucet.uo1.net/send.php
      
      * https://tbtc.bitaps.com/
      
        
      
    * 比特币脚本Debugger
      
      * https://ide.bitauth.com/
      
      * http://bitcoin-script-debugger.visvirial.com/

        
      
    * 比特币脚本资料
    
      * https://en.bitcoin.it/wiki/Script
      
        
      
    * 将 curl 请求转化为 python 代码
      
      * https://curl.trillworks.com/

   

   ## 代码实现

   完整代码：https://github.com/Hbenmazi/TimedCommitment

   **注意：**为了简化实现，我们只设置一个接收方。

   **注意：**不加说明的情况下，以下操作都默认基于比特币测试网。

   

   ### 基本功能的实现

   ​	该部分讲述了一些在实现过程中比较常用的功能和代码，以避免后续重复解释。



   #### 生成钱包地址

   * 使用 BlockCypher 的API生成地址
   
     ```curl
     curl -X POST https://api.blockcypher.com/v1/btc/test3/addrs
     ```
     
     ```python
     输出：
     {
       "private": "d9e9d07e538cd27e4bfaa712c1e7893149670c10d27fc61471b11c7a4c918169",
       "public": "03cfecd654690aaa8ab5ad5fb15818f44a3f341290f2ebf5e1c61ada78f8162844",
       "address": "mfyex4qxDmFx4fX8uA9xyNV6tjQZVxbeoN",
       "wif": "cUtJAL2nTtyBuVa3awmR42PRuWfeByquXDK6Zg6t9biLe69hLtHD"
     }
     ```
   
     
     或者
     
     ```python
     import json
     import requests
     
     response = requests.post('https://api.blockcypher.com/v1/btc/test3/addrs')
     response_content = json.loads(str(response.content, 'utf-8'))
     print('pri_key', response_content['private'])
     print('pub_key', response_content['public'])
     print('address', response_content['address'])
     ```
     
     ```python
     输出：
     pri_key d9e9d07e538cd27e4bfaa712c1e7893149670c10d27fc61471b11c7a4c918169
     pub_key 03cfecd654690aaa8ab5ad5fb15818f44a3f341290f2ebf5e1c61ada78f8162844
     address mfyex4qxDmFx4fX8uA9xyNV6tjQZVxbeoN   
     ```
     
     


   #### 创建公钥、私钥和地址对象

   ```python
   from btcpy.structs.crypto import PublicKey
   from btcpy.structs.address import P2pkhAddress, PrivateKey
   pubk_hex = '03cfecd654690aaa8ab5ad5fb15818f44a3f341290f2ebf5e1c61ada78f8162844'
   pubk = PublicKey.unhexlify(pubk_hex)
   address = P2pkhAddress(pubk.hash())
   
   privk_hex = 'd9e9d07e538cd27e4bfaa712c1e7893149670c10d27fc61471b11c7a4c918169'
   privk = PrivateKey.unhexlify(privk_hex)
   ```

   

   #### 广播交易

由于不同的比特币开发包对于 *比特币交易* ，构建了不同的数据结构，所以这里只讲述怎么广播 raw transaction 。Raw transaction 是指编码为 *十六进制* 后的交易，这种格式是通用的。

   * 方法一：人工广播
   
     将 raw transaction 复制到 https://tbtc.bitaps.com/broadcast，点击Broadcast。
   
     ![image-20200102233144765](\img\image-20200102233144765.png)
   
     
   
   * 方法二：使用 blockcypher 的 pushtx 方法
   
     ```python
     from blockcypher import pushtx
     
     tx = pushtx(coin_symbol='btc-testnet', api_key='YOUR_TOKEN', tx_hex='RAW TRANSCATION')
     print(tx)
     ```
   
     
   
   * 方法三：使用方法一中网站的API
   
     通过查看该网站的源代码可以看到它是怎么向服务器做出请求的，于是我们可以仿照着写一个广播交易的请求。
   
     ```python
     import json
     import re
     
     def broadcast_raw_tx(raw_tx):
         raw_tx = raw_tx.strip()
         if re.match('^[0-9A-Fa-f]+$', raw_tx, flags=0) is not None:
             print('Broadcasting...')
             data = {"jsonrpc": "1.0", "id": "1", "method": "sendrawtransaction", "params": 	[raw_tx]}
             response = requests.post('https://api.bitaps.com/btc/testnet/native/', data=json.dumps(data))
             response_content = json.loads(str(response.content, 'utf-8'))
             return response_content
     
         else:
             return 'Invalid HEX format'
     ```
     
     
   
   * 使用 blockcypher API 和  https://tbtc.bitaps.com/broadcast (以下简称bitaps-broadcast)的区别
   
     虽然同样是广播交易，但是这两种方法在使用中是存在区别的，尤其是在广播 $PayDeposit_{i}$ 交易时。
   
     
     
     *  使用 blockcypher API 广播 $PayDeposit_{i}$ 交易
       * 无论当前时间是否满足时间锁定的条件，该交易都会被广播
       
       * 如果该交易未满足时间锁定的条件却被广播了，那么该交易将一直不会被确认(即是一段时间过后，时间锁定条件已经满足)。并且通过 https://live.blockcypher.com/ 可以查询到该交易，但是通过  https://tbtc.bitaps.com/ 则查询不到该交易。
       
       * 如果想要该交易恢复正常，必须等待时间锁定条件满足后，通过其它方法（方法一或方法三或其它方法）重新广播完全相同的交易。
       
         
       
     *  使用 bitaps-broadcast广播 $PayDeposit_{i}$ 交易
     
        *  只有满足时间锁定的条件，该交易才能被广播成功，否则会报错
     
           
     
     *  因此，当广播 $PayDeposit_{i}$ 交易时，建议使用方法一或者方法三
     
        
     
     *  原因：初步猜测是因为这两种方法背后的机制不同。
     
        *  bitaps-broadcast 背后的服务器应该执行了挖矿程序，并且在执行途中发现了$PayDeposit_{i}$ 交易不符合条件，因此直接驳回了该交易，并能够返回相应的错误信息。
        
     * blockcypher API 背后的服务器中应该是没有矿工挖矿的程序执行的，它只是负责把交易广播给网络中的其它矿工结点，因此它根本不能够发现交易是不满足时间锁定条件的。而其他矿工结点在发现该交易不满足时间锁定条件后，很有可能会直接放弃该交易，而不是等待时间锁定条件满足。因此，即使时间已经满足了条件，还是要通过其它方法重新向网络中广播该交易。

#### 获取Raw transaction

* 通过交易的哈希人工查询

  在 https://tbtc.bitaps.com/ 上搜索交易的哈希，在[交易的详情页面](https://tbtc.bitaps.com/59ceb0cd9cb8a63ff8cc3a4c6979dcb29b2af81b267829035a5ac3d409c85e98)中点击 [Raw transaction](https://tbtc.bitaps.com/raw/transaction/59ceb0cd9cb8a63ff8cc3a4c6979dcb29b2af81b267829035a5ac3d409c85e98)。

  ![image-20200104095730755](C:\Users\QJ\AppData\Roaming\Typora\typora-user-images\image-20200104095730755.png)

* 使用 blockcypher 的get_transaction_detail 方法

  ```python
  from blockcypher import get_transaction_details
  
  def get_raw_tx(tx_hash, coin_symbol):
      tx = get_transaction_details(tx_hash, coin_symbol, include_hex=True)
      return tx['hex']
  ```


#### 解码 Raw Transaction

```python
from btcpy.structs.transaction import TransactionFactory

# raw transaction
raw_tx = '0200000001985ec809d4c35a5a032978261bf82a9bb2dc79694c3accf83fa6b89ccdb0ce59000000007b4730440220336dc455eaad9573cc25294bfbc1138c7130fb67f1833c35fac752215bdb34560220410573ded0d823dfc1827875e2b7c4f8aa16dabcf803288836a5f81774b79925012103acb78908123c649e65d5e3689c3c53c25725c6eb53a6aa7834f73127c4eb2db10f49206861766520616e206170706c6551ffffffff0102830100000000001976a9141d78b0742727857d169c0c4f17795b9f18b4b0d588ac00000000'

# decode from raw transaction and print
tx = TransactionFactory.unhexlify(raw_tx)
print(tx.to_json())
```

```python
输出：
{
  "hex": "0200000001985ec809d4c35a5a032978261bf82a9bb2dc79694c3accf83fa6b89ccdb0ce59000000007b4730440220336dc455eaad9573cc25294bfbc1138c7130fb67f1833c35fac752215bdb34560220410573ded0d823dfc1827875e2b7c4f8aa16dabcf803288836a5f81774b79925012103acb78908123c649e65d5e3689c3c53c25725c6eb53a6aa7834f73127c4eb2db10f49206861766520616e206170706c6551ffffffff0102830100000000001976a9141d78b0742727857d169c0c4f17795b9f18b4b0d588ac00000000",
  "txid": "4742ef605b1553f9d8cd400713c8b44d9094d750258e20e60a5dac6d9aed8d29",
  "hash": "4742ef605b1553f9d8cd400713c8b44d9094d750258e20e60a5dac6d9aed8d29",
  "size": 208,
  "vsize": 208,
  "version": 2,
  "locktime": 0,
  "vin": [
    {
      "txid": "59ceb0cd9cb8a63ff8cc3a4c6979dcb29b2af81b267829035a5ac3d409c85e98",
      "vout": 0,
      "scriptSig": {
        "asm": "30440220336dc455eaad9573cc25294bfbc1138c7130fb67f1833c35fac752215bdb34560220410573ded0d823dfc1827875e2b7c4f8aa16dabcf803288836a5f81774b7992501 03acb78908123c649e65d5e3689c3c53c25725c6eb53a6aa7834f73127c4eb2db1 49206861766520616e206170706c65 OP_1",
        "hex": "4730440220336dc455eaad9573cc25294bfbc1138c7130fb67f1833c35fac752215bdb34560220410573ded0d823dfc1827875e2b7c4f8aa16dabcf803288836a5f81774b79925012103acb78908123c649e65d5e3689c3c53c25725c6eb53a6aa7834f73127c4eb2db10f49206861766520616e206170706c6551"
      },
      "sequence": "4294967295"
    }
  ],
  "vout": [
    {
      "value": "0.00099074",
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 1d78b0742727857d169c0c4f17795b9f18b4b0d5 OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a9141d78b0742727857d169c0c4f17795b9f18b4b0d588ac",
        "type": "p2pkh",
        "address": "miCnUFjFhALHub5VewXv13HCy4FJ5PZrCH"
      }
    }
  ]
}
```



#### 清理资产(sweeping fund)

总所周知，一个比特币地址的余额是由比特币网络中所有指向该地址的UTXO(Unspent Transaction Output)之和决定的。例如，以下比特币地址的资产等于四个交易输出之和：

![image-20200103115445357](\img\image-20200103115445357.png) 
![image-20200103115532968](\img\image-20200103115532968.png)

   因此，如果需要创建一笔输出为 $x$ BTC的交易，必须指定上图四个交易输出中的几个作为新交易的输入，使得输入的金额大于 $x$。

解决这个问题可以有几种方法：

1. 如上图，可以通过 bitcoin exploration 类的网站查询交易。

   

2. 使用 blockcypher 的 get_address_details 方法可以获得与该地址相关的所有交易输入和输出的信息。

   ```python
   from blockcypher import get_address_details
   get_address_details('n1rR5McqgF7GHWmj4V7HFRvyvX2wAd64xp', coin_symbol='btc-testnet')
   ```

   ```python
   输出：
   {
     "address": "n1rR5McqgF7GHWmj4V7HFRvyvX2wAd64xp",
     "total_received": 4003446,
     "total_sent": 0,
     "balance": 4003446,
     "unconfirmed_balance": 0,
     "final_balance": 4003446,
     "n_tx": 4,
     "unconfirmed_n_tx": 0,
     "final_n_tx": 4,
     "txrefs": [
       {
         "tx_hash": "4cfe96079c393ff47bce909d341f1e4798ff918e6650df88f6c69306ad4438c4",
         "block_height": 1638191,
         "tx_input_n": -1,
         "tx_output_n": 0,
         "value": 1000000,
         "ref_balance": 4003446,
         "spent": false,
         "confirmations": 7,
         "confirmed": "2020-01-03 03:31:06",
         "double_spend": false
       },
       {
         "tx_hash": "b954403b90aca7c2d0c1ea6d01adb6c335cae6861641a2b97eea4ec1c009e93b",
         "block_height": 1638191,
         "tx_input_n": -1,
         "tx_output_n": 0,
         "value": 1000000,
         "ref_balance": 3003446,
         "spent": false,
         "confirmations": 7,
         "confirmed": "2020-01-03 03:31:06",
         "double_spend": false
       },
   	............
     ],
     "tx_url": "https://api.blockcypher.com/v1/btc/test3/txs/",
     "unconfirmed_txrefs": []
   }
   ```

   

3. 使用 blockchain 的 simple_spend 方法，并将 $to\_satoshis$ 参数设置为 -1 , 即可将 *输入地址* 中所有的比特币转移至 *输出地址* ，我们只需要将 *输入地址* (实际上只需要填写私钥) 和 *输出地址* 设置为同一个地址即可。

   ```python
   from blockcypher import simple_spend
   
   tx_hash = simple_spend(from_privkey='7f906474b569069d942b82bf84e0f04a1b3c761861556b028201983d8128bcce',
               to_address='n1rR5McqgF7GHWmj4V7HFRvyvX2wAd64xp', 
               to_satoshis=-1, 
               coin_symbol='btc-testnet', 
               api_key='YOUR_TOKEN')
   print(tx_hash)
   ```
   
   ```python
输出：
   'c913b2424445c1b882c8b3198f1268af672ad7e604b8c206b3c341e8715f15e7'
   ```

   
   
   于是，我们将刚刚四笔交易的钱，通过一笔交易汇合在了一起。这样在下次创建交易时，就只需要一个输入了。
   
   ![image-20200103130837452](\img\image-20200103130837452.png)



   当然，这种方法的缺点也是显而易见的：

   1. 需要时间去确认新的交易是否被网络接受
   
   2. 创建额外的交易，意味着支付额外的矿工挖矿费用
   
      ​	但出于方便并且获取测试币较为容易，我在实现时还是使用了这种方法。



#### 如何决定Mining Fee

​	交易的 mining fee 是指支付给矿工的采矿费用。其值等于交易 *输入金额* 和* 输出金额* 的差值。Mining fee 越高，矿工越有兴趣广播该交易，交易被确认得越快。

​	一般来说，交易的 size 越大需要支付的 mining fee 越多。但是交易的大小在创建完成之前很难精确计算，所以一般采用估算的方法：

​    根据搜索到的资料，普通交易的字节数可以通过其输入和输出的数量估算，公式如下：

```python
def cal_tx_size_in_byte(inputs_num, outputs_num):
    return inputs_num * 180 + outputs_num * 34 + 10
```
此外，可以通过 blockcypher 的 get_blockchain_overview 方法获得每 KB 的挖矿费用 (statoshi / kbytes)。

**注意：**$1 BTC = 10^{8}statoshi$

```python
from blockcypher import get_blockchain_overview

get_blockchain_overview(coin_symbol='btc-testet', api_key='YOUR_TOKEN')
```

```python
输出：

{
 	.........
    "high_fee_per_kb": 51535, 
    "low_fee_per_kb": 24372, 
    "medium_fee_per_kb": 29490, 
    .........
}
```

获得的三个数据的解释如下表：

| Attribute             | Type      | Description                                                  |
| :-------------------- | :-------- | :----------------------------------------------------------- |
| **high_fee_per_kb**   | *integer* | A rolling average of the fee (in satoshis) paid per kilobyte for transactions to be confirmed within 1 to 2 blocks. |
| **medium_fee_per_kb** | *integer* | A rolling average of the fee (in satoshis) paid per kilobyte for transactions to be confirmed within 3 to 6 blocks. |
| **low_fee_per_kb**    | *integer* | A rolling average of the fee (in satoshis) paid per kilobyte for transactions to be confirmed in 7 or more blocks. |

**注意：**根据我的经验，建议将以上方法得到的交易费用乘一个系数2或者3，以使交易尽可能快地得到确认。



### 定时承诺的实现

我们使用 [定时承诺介绍](#定时承诺介绍) 中介绍的 *“实现二”*  来实现定时承诺。

#### *Commit* 交易

* [创建 *Commiter* 的公钥、私钥和地址对象以及 *Recipient* 的公钥对象](#创建公钥、私钥和地址对象)

* 对秘密通过 HASH256 进行加密

  比如我们设置一个秘密是 "I have an apple"，并通过 HASH256 加密。

  **注意：** 

  1. HASH256 等价于两次 SHA256

   	2. 为了方便，这里的秘密后面没有拼接随机数

  ```python
  import hashlib
  from btcpy.structs.sig import *
  
  # a sample of secret
  secret = 'I have an apple'.encode()
  secret_hash = hashlib.sha256(hashlib.sha256(secret).digest()).digest()
  secret_hash = StackData.from_bytes(secret_hash) # StackData类表示脚本压入堆栈的数据
  print("秘密经hash256加密结果:", secret_hash)
  ```

  ```python
  输出：
  秘密经hash256加密结果: 59d47d5565ce1e8df0772e5c00abdb31b8ca140017511a8afe6ba567fb27b79d
  ```

  

* [清理资产](#清理资产(sweeping-fund))

  ```python
  # 清理资产
  # 返回交易的哈希和钱包余额
  to_spend_hash, balance = sweep_fund(privkey=privk_hex, # commiter's privket in hex format
                                      address="commiter's address", 
                                      coin_symbol='btc-testnet',
                                      api_key='YOUR_TOKEN')
  ```

  

* 创建输出脚本

  关于比特币脚本，https://en.bitcoin.it/wiki/Script 上有非常详细的解读和例子，[btcpy的文档](https://github.com/chainside/btcpy#scripts)中也有很详细的创建脚本的示例，由于篇幅原因本教程不再赘述。

  

  由于 Commiter 除了付出押金还需要把剩余的钱转回给自己，因此我们一共需要两个输出脚本。
  
  * 定时承诺输出脚本
  
    ```python
    from btcpy.structs.script import Hashlock256Script
    from btcpy.structs.sig import *
    
    # sequence(lock_time)
    sequence = 5
    
    lock_time_script = IfElseScript(
        # if branch
        Hashlock256Script(secret_hash,
                          P2pkhScript(pubk)), # pubk: committer's public key
        # else branch
        RelativeTimelockScript(  # timelocked script
            Sequence(sequence),  # expiration, 5 blocks
            P2pkhScript(pubk2)   # recipient's public key
        )
    )
    
    print("lock_time_script.type: ", lock_time_script.type)
    print("lock_time_script str: ", str(lock_time_script))
    ```
  
    ```python
    输出：
    
    lock_time_script.type:  if{ [hashlock] p2pkh }else{ [relativetimelock] p2pkh }
        
    lock_time_script str:  OP_IF OP_HASH256 59d47d5565ce1e8df0772e5c00abdb31b8ca140017511a8afe6ba567fb27b79d OP_EQUALVERIFY OP_DUP OP_HASH160 1d78b0742727857d169c0c4f17795b9f18b4b0d5 OP_EQUALVERIFY OP_CHECKSIG OP_ELSE OP_5 OP_CHECKSEQUENCEVERIFY OP_DROP OP_DUP OP_HASH160 02d07fadf17edd37bc6fbab18a2b38057560e64a OP_EQUALVERIFY OP_CHECKSIG OP_ENDIF
    # 其中59d47d55.......就是 "I have an apple" 经过HASH256的结果
    ```
  
    Sequence既可以基于时间(time_based)，也可以基于块的个数(block-based), 具体的设置要求请见[BIP68](https://github.com/bitcoin/bips/blob/master/bip-0068.mediawiki)。也可以直接使用 btcpy 中的：TimebasedSequence 或者 HeightBasedSequence 类。
  
    ​	
  
  * 找零输出脚本
  
    ```python
    # 找零脚本
    change_script = P2pkhScript(pubk)
    ```
  
  
  
* 估算Mining Fee

  ```python
  mining_fee_per_kb = get_mining_fee_per_kb(coin_symbol, api_key, condidence='high')
  estimated_tx_size = cal_tx_size_in_byte(inputs_num=1, outputs_num=2)
  mining_fee = int(mining_fee_per_kb * (estimated_tx_size / 1000)) * 2
  ```

* 设置罚金

  ```python
  penalty = 100000
  assert penalty + mining_fee <= balance, 'commiter账户余额不足'
  ```

* 获取交易输入

  ```python
  from btcpy.structs.transaction import TransactionFactory
  
  to_spend_raw = get_raw_tx(to_spend_hash, coin_symbol='btc-testnet')
  to_spend = TransactionFactory.unhexlify(to_spend_raw)
  ```

* 创建交易

  **注意：**交易的 version 参数必须为2。只有 version=2 的交易才能使用 *相对锁定时间*  功能。

  ```python
  from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
  from btcpy.structs.script import  ScriptSig
  
  unsigned = MutableTransaction(version=2,
                                ins=[TxIn(txid=to_spend.txid,			 # 上一笔交易的哈希
                                          txout=0,					# 使用第一个输出
                                          script_sig=ScriptSig.empty(), # 输入脚本为空(待修改)
                                          sequence=Sequence.max())], 	  # 0xFFFFFF
                                outs=[TxOut(value=penalty, # 金额				
                                            n=0,			# 输出编号
                                            script_pubkey=lock_time_script), # 输出脚本
                                      TxOut(value=balance - penalty - mining_fee,
                                            n=1,
                                            script_pubkey=change_script)],
                                locktime=Locktime(0))
  ```

  此时，交易的输入脚本为空。

  

* 修改交易

  ```python
  from btcpy.structs.sig import *
  
  # 输入脚本
  solver = P2pkhSolver(privk) # privk is committer's private key
  
  # 修改交易
  signed = unsigned.spend([to_spend.outs[0]], [solver]) # 指定上一笔交易(to_spend)的输出和对应的输入脚本
  print('commit_tx_hex: ', signed.hexlify())
  ```

  ```python
  输出：
  
  commit_tx_hex: 
  0200000001e3021f415eb615e05e8336e69273c6fa5925198f91806c2dff033984e436f209000000006a4730440220250640256828bf76e4e52d671c8c8c43ca900639a0e2a6424a9b69135913f78102204145f7e5b700ab8390bc74dec331165ee12991d8c6d7d48ef2f4f24b8e0736d3012103acb78908123c649e65d5e3689c3c53c25725c6eb53a6aa7834f73127c4eb2db1ffffffff02a0860100000000005b63aa2059d47d5565ce1e8df0772e5c00abdb31b8ca140017511a8afe6ba567fb27b79d8876a9141d78b0742727857d169c0c4f17795b9f18b4b0d588ac6755b27576a91402d07fadf17edd37bc6fbab18a2b38057560e64a88ac68e0480200000000001976a9141d78b0742727857d169c0c4f17795b9f18b4b0d588ac00000000
  ```

  

 * [广播交易](#广播交易)

   ```python
   from blockcypher import pushtx
   tx = pushtx(coin_symbol=coin_symbol, api_key=api_key, tx_hex=signed.hexlify())
   print(tx)
   ```

   ```python
   输出：
   {
     "tx": {
       "block_height": -1,
       "block_index": -1,
       "hash": "59ceb0cd9cb8a63ff8cc3a4c6979dcb29b2af81b267829035a5ac3d409c85e98",
       "addresses": [
         "miCnUFjFhALHub5VewXv13HCy4FJ5PZrCH"
       ],
       "total": 249728,
       "fees": 878,
       "size": 291,
       "preference": "low",
       "relayed_by": "221.4.34.18",
       "received": "2020-01-03T15:21:12.059432676Z",
       "ver": 2,
       "double_spend": false,
       "vin_sz": 1,
       "vout_sz": 2,
       "confirmations": 0,
       "inputs": [
         {
           "prev_hash": "09f236e4843903ff2d6c80918f192559fac67392e636835ee015b65e411f02e3",
           "output_index": 0,
           "script": "4730440220250640256828bf76e4e52d671c8c8c43ca900639a0e2a6424a9b69135913f78102204145f7e5b700ab8390bc74dec331165ee12991d8c6d7d48ef2f4f24b8e0736d3012103acb78908123c649e65d5e3689c3c53c25725c6eb53a6aa7834f73127c4eb2db1",
           "output_value": 250606,
           "sequence": 4294967295,
           "addresses": [
             "miCnUFjFhALHub5VewXv13HCy4FJ5PZrCH"
           ],
           "script_type": "pay-to-pubkey-hash",
           "age": 0
         }
       ],
       "outputs": [
         {
           "value": 100000,
           "script": "63aa2059d47d5565ce1e8df0772e5c00abdb31b8ca140017511a8afe6ba567fb27b79d8876a9141d78b0742727857d169c0c4f17795b9f18b4b0d588ac6755b27576a91402d07fadf17edd37bc6fbab18a2b38057560e64a88ac68",
           "addresses": null,
           "script_type": "unknown"
         },
         {
           "value": 149728,
           "script": "76a9141d78b0742727857d169c0c4f17795b9f18b4b0d588ac",
           "addresses": [
             "miCnUFjFhALHub5VewXv13HCy4FJ5PZrCH"
           ],
           "script_type": "pay-to-pubkey-hash"
         }
       ]
     }
   }
   ```

   根据交易的哈希我们可以在网站中搜索到该交易：
   
   https://tbtc.bitaps.com/59ceb0cd9cb8a63ff8cc3a4c6979dcb29b2af81b267829035a5ac3d409c85e98
   
   可以看到该交易有一个输入，两个输出。第一个输出是非标准的脚本即定时承诺的脚本，第二个输出是标准的 pay-to-pubkey-hash 脚本。
   
   ![image-20200104100949635](\img\image-20200104100949635.png)
   
   ![image-20200104101023911](\img\image-20200104101023911.png)



#### *Open* 交易

##### 创建并广播 *Open* 交易

* [创建 *Commiter* 的公钥、私钥对象](#创建公钥、私钥和地址对象)

* 准备好秘密的*原像*， 创建输入脚本和输出脚本

  ```python
  from btcpy.structs.sig import IfElseSolver, HashlockSolver, P2pkhSolver, Branch
  
  # 创建输入脚本
  secret = 'I have an apple'  # 需要展示的秘密
  p2pkh_solver = P2pkhSolver(privk)
  hasklock_solver = HashlockSolver(secret.encode(), p2pkh_solver)
  if_solver = IfElseSolver(Branch.IF,  # branch selection
                           hasklock_solver)
  # 创建输出脚本
  script = P2pkhScript(pubk)
  ```

* 准备好上一笔交易，获取押金的数额

  ```python
  from btcpy.structs.transaction import TransactionFactory
  
  to_spend_hash = "Commit 交易的hash"
  to_spend_raw = get_raw_tx(to_spend_hash, coin_symbol)
  to_spend = TransactionFactory.unhexlify(to_spend_raw)
  penalty = int(float(to_spend.to_json()['vout'][0]['value']) * (10**8))
  ```

* 估算Mining Fee，创建交易，修改输入脚本

  ```python
  from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
  from btcpy.structs.script import  ScriptSig
  
  # 估算 Mining Fee
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
  
  # 修改输入脚本
  signed = unsigned.spend([to_spend.outs[0]], [if_solver])
  ```

 * 广播交易

   ```python
   from blockcypher import pushtx
   
   msg = pushtx(coin_symbol='btc-testnet', api_key='YOUR_TOKEN', tx_hex=signed.hexlify())
   print(msg)
   ```

   ```python
   输出：
   {
     "tx": {
       "block_height": -1,
       "block_index": -1,
       "hash": "4742ef605b1553f9d8cd400713c8b44d9094d750258e20e60a5dac6d9aed8d29",
       "addresses": [
         "miCnUFjFhALHub5VewXv13HCy4FJ5PZrCH"
       ],
       "total": 99074,
       "fees": 926,
       "size": 208,
       "preference": "low",
       "relayed_by": "221.4.34.170",
       "received": "2020-01-04T02:39:38.239402344Z",
       "ver": 2,
       "double_spend": false,
       "vin_sz": 1,
       "vout_sz": 1,
       "confirmations": 0,
       "inputs": [
         {
           "prev_hash": "59ceb0cd9cb8a63ff8cc3a4c6979dcb29b2af81b267829035a5ac3d409c85e98",
           "output_index": 0,
           "script": "4730440220336dc455eaad9573cc25294bfbc1138c7130fb67f1833c35fac752215bdb34560220410573ded0d823dfc1827875e2b7c4f8aa16dabcf803288836a5f81774b79925012103acb78908123c649e65d5e3689c3c53c25725c6eb53a6aa7834f73127c4eb2db10f49206861766520616e206170706c6551",
           "output_value": 100000,
           "sequence": 4294967295,
           "script_type": "unknown",
           "age": 1638254
         }
       ],
       "outputs": [
         {
           "value": 99074,
           "script": "76a9141d78b0742727857d169c0c4f17795b9f18b4b0d588ac",
           "addresses": [
             "miCnUFjFhALHub5VewXv13HCy4FJ5PZrCH"
           ],
           "script_type": "pay-to-pubkey-hash"
         }
       ]
     }
   }
   ```
   

   
   通过[查询这笔交易](https://tbtc.bitaps.com/4742ef605b1553f9d8cd400713c8b44d9094d750258e20e60a5dac6d9aed8d29)可以看到 Committer 取回了罚金：
   
   ![image-20200104104514251](\img\image-20200104104514251.png)



##### 查看秘密

* 获取 *Open* 交易

  ```python
  from btcpy.structs.transaction import TransactionFactory
  
  # 获取Open交易
  open_tx_hash = '4742ef605b1553f9d8cd400713c8b44d9094d750258e20e60a5dac6d9aed8d29'  # open交易的hash
  raw_open_tx = get_raw_tx(open_tx_hash, coin_symbol)
  open_tx = TransactionFactory.unhexlify(raw_open_tx)  # decode raw transaction
  open_tx = open_tx.to_json()
  ```

  

* 处理 *Open* 交易的输入脚本

  ```python
  # 获取输入脚本
  scriptSig = open_tx['vin'][0]['scriptSig']['asm']
  
  # 将输入脚本按空格分割
  scriptSig_list = scriptSig.split()
  ```

  

* 获取 *秘密*  并进行解码

  ```python
  # 如无意外，秘密应该在脚本的倒数第二个位置
  secret_hex = scriptSig_list[-2]
  
  # 从hex将秘密解码出来
  print('secret hex: ', secret_hex)
  print('decoded secret: ', bytes.fromhex(secret_hex).decode())
  ```

  ```python
  输出：
  secret hex:  49206861766520616e206170706c65
  decoded secret:  I have an apple
  ```



#### *PayDeposit* 交易

当 Committer 超过了时间限定却还没有执行 *Open*交易 时，Recipient可以执行 *PayDeposit*交易 获取 Committer 支付的押金。

这里我重新创建并广播了 [Commit 交易](https://tbtc.bitaps.com/bcf352c53d01bd0e33e7d3a9eb70ca8492d335c4d3d84a93b301066ce953e974) ，它的txid为:

```python
commit_tx_hash = 'bcf352c53d01bd0e33e7d3a9eb70ca8492d335c4d3d84a93b301066ce953e974'
```



##### 创建交易

* [创建 Recipient 的公钥和私钥对象](#创建公钥、私钥和地址对象)

* 获取 *Commit* 交易以及罚金数额

  ```python
  from btcpy.structs.transaction import TransactionFactory
  
  # 获取 commit 交易
  to_spend_hash = commit_tx_hash # commit交易的hash
  to_spend_raw = get_raw_tx(to_spend_hash, coin_symbol='btc-testnet')
  to_spend = TransactionFactory.unhexlify(to_spend_raw)
  
  # 获取罚金数额
  penalty = int(float(to_spend.to_json()['vout'][0]['value']) * (10**8))
  ```

  

* 创建输出脚本计算mining fee

  ```python
  from btcpy.structs.script import P2pkhScript
  
  # 输出脚本
  script = P2pkhScript(pubk) # pubk为 Recipient 的公钥
  
  # 计算挖矿费用
  mining_fee_per_kb = get_mining_fee_per_kb(coin_symbol, api_key, condidence='high')
  estimated_tx_size = cal_tx_size_in_byte(inputs_num=1, outputs_num=1)
  mining_fee = int(mining_fee_per_kb * (estimated_tx_size / 1000)) * 2
  ```

  

* 创建交易

  ```python
  from btcpy.structs.transaction import TxIn, Sequence, TxOut, Locktime, MutableTransaction
  from btcpy.structs.script import  ScriptSig
  
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
  ```

  

* 创建输入脚本，修改交易

  ```python
  from btcpy.structs.sig import IfElseSolver, P2pkhSolver, Branch, RelativeTimelockSolver
  
  # 输入脚本
  else_solver = IfElseSolver(Branch.ELSE, # Branch selection
                             RelativeTimelockSolver(Sequence(5), P2pkhSolver(privk))) # privk为 Recipient 的私钥
  
  # 修改交易
  signed = unsigned.spend([to_spend.outs[0]], [else_solver])
  ```

  **注意：** 对于 *RelativeTimelockSolver* 中的第一个参数 *Sequence($x$)*， 应至少使 $x$ 大于等于 [*Commit* 交易](#*Commit* 交易) 中设置的sequence参数的值(上文中设置为5)，这里是解除 *时间锁定* 的地方。当然，一般设置为等于即可。



##### 广播交易

```python
# 广播交易
print('pay_desposit_hex:', signed.hexlify())
msg = broadcast_raw_tx(signed.hexlify())
print(msg)
```

**注意：**这里请用[广播交易](#广播交易)中的 **方法三** 进行广播。



###### 未解除时间锁定

假设在规定的时间之前，Recipient 想提前获得押金，那么比特币网络将驳回 *PayDeposit* 交易。

```python
# 未解除时间锁定时的输出：
{
  "result": null,
  "error": {
    "code": -26,
    "message": "non-BIP68-final (code 64)"
  },
  "id": "1"
}
```

出现了错误代码：-26 和 错误信息："non-BIP68-final (code 64)"

根据 [比特币RPC的源代码](https://github.com/bitcoin/bitcoin/blob/62f2d769e45043c1f262ed45babb70fe237ad2bb/src/rpc/protocol.h#L30):

```c
enum RPCErrorCode
{
    .........
    RPC_VERIFY_REJECTED             = -26, //! Transaction or block was rejected by network rules
    .........
};
```

code：-26 对应的错误的原因是：*交易或者区块根据比特币网络的规则被驳回*



进一步在 [比特币验证交易的源码](https://github.com/bitcoin/bitcoin/blob/1f8378508acfc1f6ca48dcc75eb0848e82bb183d/src/validation.cpp#L1362) 中搜索 "non-BIP68-final (code 64)" 可以得到：

```c
.........
return (ValidationInvalidReason::TX_PREMATURE_SPEND, false, 			               REJECT_NONSTANDARD, "non-BIP68-final");
```

可见，该交易验证为无效的原因是：TX_PREMATURE_SPEND，即交易 *过早地* 被花费。这正是我们希望看到的结果。



###### 成功解除时间锁定

等待 *Commit* 交易的确认数到达 5 个(或以上)的时候，重新广播 *PayDeposit* 交易

![image-20200104153758476](\img\image-20200104153758476.png)

```python
# 成功解除时间锁定时的输出：
{
  "result": "dd00307873009574c0536b71ad776370423c814052ba551f6848af942cf1d902",
  "error": null,
  "id": "1"
}
```

其中 *error* 为 null，交易被成功广播，result字段是交易的hash。



通过hash值搜索交易，可以看到 Recipient 已经获得了押金：

![image-20200104154123024](\img\image-20200104154123024.png)

