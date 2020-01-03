# TimedCommitment
The implementation of bitcoin-based timed-commitment scheme from "Secure Multiparty Computations on Bitcoin"

定时承诺的实现
==============

定时承诺介绍
----------------

​	承诺过程包括两个阶段：承诺阶段和开启阶段。通常来说，承诺在两方之间执行：承诺方C和接受方。更一般地说，我们可以假设有n个接受者，表示为$P_1, ...,P_n$. 

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
  
      <img src="E:\browser download\a8ea7cd1861db26ac5c2b4d4cdb1cf02_1_2_art.png" alt="a8ea7cd1861db26ac5c2b4d4cdb1cf02_1_2_art" style="zoom:130%;" />
      
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
    

环境准备
--------------

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
      
        
      
    * 将 curl 请求转化为 python 代码
      
      * https://curl.trillworks.com/

   

   ## 代码实现

   完整代码：https://github.com/Hbenmazi/TimedCommitment

   **注意：**为了简化实现，我们只设置一个接收方。

   **注意：** 不加说明的情况下，以下操作都默认基于比特币测试网。

   

   ### 基本功能的实现

   ​	该部分讲述了一些在实现过程中比较常用的功能和代码，以避免后续重复解释。

   

   #### 生成钱包地址

   * 使用 BlockCypher 的API生成地址
   
     ```
     curl -X POST https://api.blockcypher.com/v1/btc/test3/addrs
     
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
   
     将 raw transaction 复制到 https://tbtc.bitaps.com/broadcast，点击Boardcast。
   
     ![image-20200102233144765](C:\Users\QJ\AppData\Roaming\Typora\typora-user-images\image-20200102233144765.png)
   
     
   
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
     
     def boardcast_raw_tx(raw_tx):
         raw_tx = raw_tx.strip()
         if re.match('^[0-9A-Fa-f]+$', raw_tx, flags=0) is not None:
             print('Boardcasting...')
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

#### 清理资产(sweeping fund)

总所周知，一个比特币地址的余额是由比特币网络中所有指向该地址的UTXO(Unspent Transaction Output)之和决定的。例如，以下比特币地址的资产等于四个交易输出之和：

![image-20200103115445357](C:\Users\QJ\AppData\Roaming\Typora\typora-user-images\image-20200103115445357.png) 
![image-20200103115532968](C:\Users\QJ\AppData\Roaming\Typora\typora-user-images\image-20200103115532968.png)

   因此，如果需要创建一笔输出为 $x$ BTC的交易，必须指定上图四个交易输出中的几个作为新交易的输入，使得输入的金额大于 $x$。

解决这个问题可以有几种方法：

1. 如上图，可以通过 bitcoin exploration 类的网站查询交易。

   

2. 使用 blockcypher 的 get_address_details 方法可以获得与该地址相关的所有交易输入和输出的信息。

   ```python
   from blockcypher import get_address_details
   get_address_details('n1rR5McqgF7GHWmj4V7HFRvyvX2wAd64xp', coin_symbol='btc-testnet')
   
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
   
   'c913b2424445c1b882c8b3198f1268af672ad7e604b8c206b3c341e8715f15e7'
   ```

   

   于是，我们将刚刚四笔交易的钱，通过一笔交易汇合在了一起。这样在下次创建交易时，就只需要一个输入了。

   ![image-20200103130837452](C:\Users\QJ\AppData\Roaming\Typora\typora-user-images\image-20200103130837452.png)

   

   当然，这种方法的缺点也是显而易见的：

   	1. 需要时间去确认新的交易是否被网络接受
    	2. 创建额外的交易，意味着支付额外的矿工挖矿费用

   但出于方便并且获取测试币较为容易，我在实现时还是使用了这种方法。

#### 获取 Raw transaction

```python
from blockcypher import get_transaction_details

def get_raw_tx(tx_hash, coin_symbol):
    tx = get_transaction_details(tx_hash, coin_symbol, include_hex=True)
    return tx['hex']
```

#### 如何决定Mining Fee

​	交易的 mining fee 是指支付给矿工的采矿费用。其值等于交易输入金额减去输出金额得到的差值。Mining fee 越高，矿工越有兴趣广播该交易，交易被确认得越快。

​	一般来说，交易的 size 越大需要支付的 mining fee 越多。但是交易的大小在创建完成之前很难精确计算，所以一般采用估算的方法：

根据搜索到的资料，普通交易的字节数可以通过其输入和输出的数量估算，公式如下：

```python
def cal_tx_size_in_byte(inputs_num, outputs_num):
    return inputs_num * 180 + outputs_num * 34 + 10
```
此外，可以通过 blockcypher 的 get_blockchain_overview 方法获得每 KB 的挖矿费用 (statoshi / kbytes)

```python
from blockcypher import get_blockchain_overview

get_blockchain_overview(coin_symbol='btc-testmet', api_key='YOUR_TOKEN')

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

