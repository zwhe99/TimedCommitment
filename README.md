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

    * BlockCypher是一个简单高效的，用于与区块链进行交互的api。可以通过[api.blockcypher.com](https://api.blockcypher.com/v1/btc/main)，使用HTTP或HTTPS访问。
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
   
   为了简化实现，我们只设置一个接收方。
   
   **注意：** 不加说明的情况下，以下操作都默认基于比特币测试网。
   
   ### 生成钱包地址
   
   * 使用 BlockCypher 的API生成地址
   
     ```
     curl -X POST https://api.blockcypher.com/v1/btc/test3/addrs
     
     {
     "private": "81ee75559d37cbe4b7cbbfb9931ab1ba32172c5cdfc3ac2d020259b4c1104198",
     "public": "0231ff9ec76820cb36b69061f6ffb125db3793b4aced468a1261b0680e1ef4883a",
     "address": "mvpW7fMSi1nbZhJJDySNS2PUau8ppnu4kY",
     "wif": "cRwGhRjCuuNtPgLcoYd1CuAqjFXCV5YNCQ1LB8RsFCvu61VfSsgR"
     }
     ```
   
     或者
   
     ```python
     >>>import json
     >>>import requests
     
     >>>response = requests.post('https://api.blockcypher.com/v1/btc/test3/addrs')
     >>>response_content = json.loads(str(response.content, 'utf-8'))
     >>>print('pri_key', response_content['private'])
     >>>print('pub_key', response_content['public'])
     >>>print('address', response_content['address'])
     ```
   
     
   
   
   
   
   
   
   
   
   
   
   
   
   
    
