---
layout: post
title: "The Basic of Scalable Cache Coherence"
description: "My homework to introduce the basic of scalable cache coherence."
category: technology
tags: [parallel, cache]
---
{% include JB/setup %}

我在计算机并行体系结构的课程上对高速缓存一致性进行了介绍。准备过程中我阅读了老师推荐的论文和书籍，也在互联网上查阅很多资料。

我准备的内容基本涵盖了缓存一致性的大部分基础知识，包括基于监听和基于目录式的缓存一致性协议的概念及权衡因素，并介绍了斯坦福的DASH协议和基于目录的协议内存占用过大的优化方案，最后还探讨了伪共享和空间局部性对性能影响。

这些偏底层的技术还是让我花了不少时间，应该庆幸自己不是基于硬件来做设计和开发。立竿见影的收获是提供了机器的视角给我，对于以前不太理解的多线程技巧也似乎找到了一些感觉。并外《并行计算机体系结构——硬件/软件结合的设计和分析》这本书内容很好，论述也清晰，神奇的是1998年出版的书到现在也没有过时。

下面就是我做的演示文稿:)

- - -

##The Role of Cache
1. Reducing the average memory access time
2. Reducing the bandwidth requirement

![figure-1]({% image_url common-memory-hierarchies-found-in-multiprocessors.png %})

从存储器层次上看，程序员对存储器容量和速度的期望是无限的，但是和存储器的成本相矛盾。每一层都要从一个较大的存储器空间中把地址映射到一个较小的但是更快上层容器。而高速缓存就是介于CPU、寄存器与主存之间的一层。

而高速缓存总是扮演着重要角色，对于处理器而言，高速缓存可以减少平均数据访问的时间。而对于共享的互连设备和存储系统而言，可以减少每个处理器需要的通信带宽。

图中表明了四类层次模型，与多处理器的规模相对应。

- (a) 图中是互连设备位于处理器和共享的一级高速缓存之间，而高速缓存连接到共享主存子系统上。处理器数量相对较少2-8个。
- (b) 图中是在基于总线的共享存储方式下，互连设备是共享总线，位于处理器的私有缓存和共享的主存子系统之间。适用于中小规模，可以支持20-30个处理器。
- (c) 图中，互连设备不一定是总线，而是点对点的互连网络。同时主存储器划分为许多的逻辑模块，并接入互连网络。这方式仍然是具有均匀的存储器访问模型。
- (d) 图中是分布式的存储方式，非对称的。可扩展的互联设备位于处理器节点之间，数据分散到每个处理器的本地主存中，由于处理器的私有缓存可以尽量减少跨网络的数据访问。

####名词解释
- DSM : 分布式共享存储器 ( Distributed shared memory )
- SMP : 对称多处理器技术 ( Symmetric multiprocessing )
- CC-NUMA : 一致性高速缓存非均匀存储访问模式 ( Cache Coherent Non-Uniform Memory Architecture )。主存在物理上是分布的，具有非均匀的访问代价，其每个节点可以看作SMP，实际上是一个DSM多处理机系统。

- - -

##The Cache Coherence Problem
* Pervasive and performance critical in multiprocessors.
* Each read should return the latest value written to that location.

![figure-2]({% image_url example-cache-coherence-problem.png %})
_Write back cache_ or _Write through cache_ ?   
_Write invalidate_  or _Write update_ ？

多处理器中的高速缓存一致性问题是普遍存在的，而且对计算机性能有着重大的影响。其中缓存一致性 （ Cache Coherence ) 保证的是： __总是能读到最新写入的值__。

如图所示，每个处理器至少有一级的私有高速缓存，那么存储块的副本出现在一个或多个处理器的高速缓存中，那么怎么保证访问的是最新写入的值正是我们本文讨论的问题。

面对高速缓存一致性问题，有两个基本的取舍点：

- 通知机制：写失效协议 或者 写更新协议
- 写入类型：直写式高速缓存(写直达）或者 写回式高速缓存

对于__通知机制__ ： 由于写更新协议必须将所有的写操作广播给共享的高速缓存，需要更大的带宽。而且对于进程迁移后，没有必要更新的缓存在没有置换前也会一直更新。所以近期的多处理器都会选择执行写失效协议。

对于__写入类型__ ： 写直达查找高速缓存最新值非常容易，但是对互连设备的带宽要求比较高，所以大多数处理器方案并不会采用。但是对于写回式，会引入更多的复杂性。多个处理器写入单元u，最终到达主存的值由包含u的高速缓存替换顺序决定，而与各处理器对u进行写操作顺序无关。所以采用写回式需要设计相应的协议来保证。

我们下面重点集中关注基于写失效和写回式的缓存一致性问题。

- - -

##Coherency vs. Consistency
Cache coherency and consistency define the action of the processors to maintain coherence.

* `Coherency` defines what value is returned on a read
* `Consistency` defines when it is available

这里需要澄清两个概念：

- Coherency (缓存一致性)
  * 缓存一致性需要保证读时需要保证什么值，总是返回最新写入的值。
  * 写操作是串行，按顺序写入a、b，读出的顺序不能为b、a。

- Consistency (存储一致性)
  * 存储一致性需要保证一个值什么时候才能读取。
  * 需要建立存储一致性(同一性, Consistency)模型，模型从严格到宽松。越宽松也就越要程序员来显式地使用同步原语、原子操作来保证一致性。

- - -

##Cache Coherence protocols

###Snooping
1. The caches are all accessible via some __broadcast__ medium (a bus or switch)
2. All cache controllers __monitor or snoop__ on the medium to determine whether or not they have a copy of a block that is requested

###Directory Based
1. The sharing status of a block of physical memory is kept in just one location, called the __directory__
2. using __point-to-point messages__ sent between the processors and memories to keep caches consistent

保证高速缓存一致性的协议通常有两个: 监听式和基于目录

监听式的协议 ，通过在总线上广播来在获得高速缓存。处理器的缓存控制器通过在总线上监听来发现是否在缓存中有副本。总线的根本性质是: 总线是连接几台设备的单独一组导线，其中每一设备可以观察到每一个总线事务，这就是一种广播形式。正如前面所说，这种集中式总线架构的规模在20-30个处理器，多于的话就会出现瓶颈。

对于基于目录的协议，该协议保存了每个缓存行的状态，称之为目录。目录中的信息包括哪个缓存行拥有该块的副本、是否处于脏状态等。通过对目录的查询，可以通过点到点的通讯来维护缓存一致性，从而避免广播。为了防止目录成为瓶颈，可以使目录本身也随着缓存存储器来分布，从而更易扩展。

- - -

##Snooping
* Single physical address space with uniform memory access (UMA) times.
* The bus severs an arbitrator for serializing accesses to a shared line.
* All caches see the same sequence of writes.
* The cache coherence traffic creates another limit on the scale and the speed of the processors. 
![figure-3]({% image_url snoopy-cache-coherent-multiprocessor.png %})

- 处理读缺失 ： 实现写失效协议的关键是使用总线或其他广播媒介来完成无效操作。处理器首先取得总线控制权然后广播无效数据的地址。所有处理器监听后检查是否存在副本，如果有则设置无效。

- 处理共享未写回的缓存行的写操作 : 向一个共享块执行写操作时，写操作需要获得对总线的访问权才能广播无效性操作。如果两个处理器同时对一个共享块进行写操作，其广播无效操作的请求会通过总线仲裁实现串行化。

- - -

##MESI (Illinois) Protocol
![figure-4]({% image_url state-transition-diagram-for-the-Illinois-MESI-protocol.png %})

###States
* Modified
* Exclusive
* Shared
* Invalid

###Requests by processors
* PrRd
* PrWr

###Actions by bus
* BusRd
* BusRdX
* BusWB

监听式协议是一种分布式算法，由一组相互作用的有限状态自动机来表示。高速缓存控制器中有两套输入：
1. 由处理器发出的存储器请求。
2. 总线监听器为了通知其它高速缓存而发起的总线事务。

MESI协议可以分为四个状态：M (已修改的)、S (共享的)、E (独占的)、I (失效的)

处理器发起的请求：读请求(PrRd)、写请求(PrWr)
总线引起的动作：

- 总线读(BusRd)：这过程由高速缓存扑空的PrRd产生。高速缓存控制器将地址放在总线上， 请求一个只读的拷贝。
- 总线排它说(BusRdx)：这个过程由写请求产生，PrWr要读的存储块要么不在高速缓存中，或者在但是不处于M 状态。请求一个它要修改的排它拷贝，主存储器(或者其它高速缓存)提供后，其它的缓存将失效，一旦高速缓存得到了排它拷贝，写操作就可以在高速缓存中完成。
- 总线写(BusWB)：由高速缓存控制器在回写时产生。

这里有三点需要澄清：

- 为什么需要总线排它读，而不是直接写呢？因为协议中是以缓存行为单位的，写入时需要获得缓存行的其他数据再进行写入，来保证同一时刻只有一个缓存行存在脏数据。
- MESI协议和MSI协议相比，引入了 E 状态，所以需要共享信号 S，来判断数据在高速缓存中是否是独占的。
- 在BusRd中，由主存储器来提供读丢失的数据。而在Illinois原始版本中提供数据的是缓存，这需要一种缓存到缓存的技术。比如当缓存是SRAM，主存是DRAM，前者比较快。

- - -

##Directory Based
* Coherence state maintained in a directory associated with memory
* Requests to a memory block do not need broadcasts
![figure-5]({% image_url a-scalable-multiprocessor-with-directories.png %})

我们的讨论主要是基于分布式存储器多处理系统。正如监听协议一样，目录协议也必须实现两个操作 : 处理读缺失和处理共享未写回的缓存行的写操作。为了实现这些操作，目录必须跟踪每个缓存行的状态。

- - -

##Example: DASH
![figure-6]({% image_url block-diagram-of-a-2x2-bash-prototype.png %})

下面我们以斯坦福经典的DASH协议为例子来说明基于目录式缓存一致性协议。

这种结构是由一定数目的处理结点构成的，结点之间通过一个高带宽、低延迟的互连网络连接。DASH系统的可扩展性要求尽量避免广播，而且不依赖于任何具体的网络拓扑结构。

- - -

##The Stanford DASH Prototype

- Directory Architecture for Shared memory
- rchitecture consists of many clusters
    * Each cluster contains 4 processors
    * Processor caches
        - L1I : 64 KB, direct mapped
        - L1D : 64 KB, direct-mapped, write-through
        - L2  : 256 KB, direct-mapped, write-back
        - 4-word write buffer
    * Snooping implemented within a cluster (MESI)
    * Directory-based implemented  between the clusters (full bit vector)
- Mesh interconnected network
![figure-7]({% image_url dash-architecture.png %})


DASH每个节点(cluster) 是由4个高性能处理器组成，物理存储器分布在各结点中，每个结
点都可访问整个存储器。处理器组内的高速缓存间是利用基于总线的监听方案来维持一致
性，而组间则利用分布式基于目录的一致性协议维持高速缓存一致性。

每个处理器有两级缓存，其中2级缓存的作用是改变1级缓存写直达的缓存策略为写回式策略，并为总线监听提供额外的缓存标记。2级缓存监听总线并维护了节点内的高速缓存一致性，采用Illinois协议。

总线提供了总线到缓存，缓存到缓存的传输能力。因为不支持对跨节点访问的分离事务，将MPBUS协议扩展，支持重发机制。为了避免不必要的重发，发送请求的处理器从仲裁器屏蔽掉，直到对方答复的消息到达，缓存后再将处理器解开屏蔽，重发请求后获得所请求的远程数据。

目录控制器主要维护了节点间的缓存一致性，并提供了到互联网络的接口。

- - -

##DASH Directory board
![figure-8]({% image_url directory-board-block-diagram.png %})

目录控制板器是单块印刷电路，上面有五个主要部件：

- DC：目录控制器，含有对应于该处理器组内的内存的目录存储器，还负责转发对远程组的请求和回应。
- PCPU：伪CPU，代表远程组CPU。负责转发和缓存远程组CPU的请求并沿着组内总线将请求发送出去。
- RC：响应控制器，负责追踪本地组一些未完成的请求并接受从远程组返回的相应的相应回应。
- Mesh * 2：互联网络是由一组mesh网络构成，分别用来处理请求和回应的。

目录存储器有一组目录项组成，每个存储块对应一项。目录项是由一位状态组 (1 bit) 和一个指针位向量 (16 bits) 组成。其中使用位向量来维护哪个节点拥有内存块的副本，状态位来记录是否有一个共享或者独占的节点。DC会随着访问内存的事务一起访问目录存储项并决定其在网络上发送的消息或产生的动作。

RC中还维护了RAC (remote access cache)，RAC是保存当前未完成的状态，并以处理器第5块高速缓存缓存了远程组返回的数据，并且等待远程回应的处理器解开总线屏蔽，RAC在通过高速缓存间传输提供数据。RAC和本地组的四个处理器的缓存一起组成了五路组关联的缓存。

- - -

##DASH Coherence Protocol
* Terminology
    - Local cluster
    - Home cluster
    - Remote cluster
    - Local memory
    - Remote memory
* Invalidation-based protocol
* Cache states: invalid, shared, and dirty
* Directory state (for all local memory blocks)
    - Uncached-remote: not cached by any remote cluster
    - Shared-remote: Cached, unmodified, by one or more remote clusters
    - Dirty-remote: Cached, modified, by one remote cluster
* Owning cluster for a block is the home cluster except if dirty-remote
* Owning cluster responds to requests and updates directory state

针对处理器组和存储器，有以下的概念：

- 本地组(Local cluster)：发起一个给定请求的某处理器组
- 总部组(Home cluster)：给定物理地址的主存和目录所在的处理器组
- 远程组(Remote cluster)：除了以上两种之外的其它处理器组
- 拥有组(Owing cluster)：缓存包含数据副本的处理器组
- 当地存储器(Local memory)：是与当地组相关联的那部分主存
- 远程存储器(Remote memory)：是那些总部不在本地的其它存储器

一个存储器块的状态有三种：

- Uncached-remote：即所有的远程组的高速缓存都不含此块的副本
- Shared-remote：有一个或多个远程组含有此块副本且副本块与存储器块是一致的
- Dirty-remote：仅有一个远程组含有此块，此块已经修改，与存储器相应的块不一致。

- - -

##Read Requests
* Initiated by CPU load instruction
* If address is in L1 cache, L1 supplies data – otherwise, fill request sent to L2
* If address is in L2, L2 supplies data – otherwise, read request sent on bus
* If address is in the cache of another processor in the cluster or in the RAC, that cache responds
    - Shared: data transferred over the bus to requester
    - Dirty: data transferred over bus to requester, RAC takes ownership of cache line
* If address not in local cluster, processor retries bus operation, and request is sent to home cluster, RAC entry is allocated
* If the block is in an uncached-remote or shared-remote state the directory controller sends the data over the reply network to the requesting cluster. 
* Requests to remote memory with directory in dirty-remote state explained in the figure
![figure-9]({% image_url flow-of-Read-Request-to-remote-memory-with-directory-in-dirty-remote-state.png %})

- - -

##Read-Exclusive Requests
* Initiated by CPU store instruction
* Data written through L1 and buffered in a write buffer
* If L2 has ownership permission, write is retired. otherwise, read-exclusive request sent on local bus
    - Write buffer is stalled
* If address is in "dirty" in one of the caches in the cluster or in the RAC
    - Owning cache sends data and ownership to requester
    - Owning cache invalidates its copy
* If address not in local cluster
    - Processor retries bus operation
    - Request is sent to home cluster
    - RAC entry is allocated
* If the memory block is in an uncached-remote the data and ownership are immediately sent back over the reply network.
* Requests to remote nodes in shared-remote state explained in the figure
* Requests to remote nodes in dirty-remote state explained in the figure
![figure-10]({% image_url flow-of-read-exclusive-request-to-remote-memory-with-directory-in-shared-remote-state.png %})
![figure-11]({% image_url flow-of-read-exclusive-request-to-remote-memory-with-directory-in-dirty-remote-state.png %})

- - -

##Other Implementation Details
* Writeback requests: When a dirty block is replaced
    - Home is local cluster: Write data to main memory
    - Home is a remote cluster: Send data to home which updates memory and state as "uncached-remote"
* Exception conditions
    - Request to a dirty block of a remote cluster after it gave up ownership
    - Ownership bouncing back and forth between two remote clusters while a third cluster requests block
    - Multiple paths in the system lead to requests being received out of order
* DeadLock and Error Handling
* Amount of information stored in directory affects scalability
    - For each memory block, DASH stores state and bit vector for other processors
    - For a more scalable system, overhead needs to be lower

- - -

##Directory Schemes
* Full Bit Vector Scheme (need $$ P^2 * M / B $$ bits)
* Cache-Based Linked List Schemes
* Limited Pointer Schemes
    - log2P bits per pointer, need $$ (i \times log_2^P) \times (P \times M/B) $$ bits
    - How to deal with the pointer overflow?
        * Limited Pointers with Broadcast Scheme ($$ Dir_i B $$)
        * Limited Pointers without Broadcast Scheme ($$ Dir_i NB $$)
        * Limited Pointers superset Scheme ($$ Dir_i X $$)

目录的组织通常分为两种方案：基于指针的方案和基于链表的方案。

DASH的原型系统使用的基于指针的 Full Bit Vector 的方案来记录目录信息，但是其内存随着处理器数量的平方而线性增加。

除此之外，也可以通过双向链表把目录信息维护在缓存中，这样虽然减低了内容的开销。但是复杂性极大地增加，尤指的是维护链表的时间复杂度和实现的难度。

所以就采用优化过的有限指针的方案，指的是不保存所有处理器的信息，而保存有限个。
但是这时就需要解决指针数量溢出的问题：

* $$ Dir_i B $$ 设置广播位，当发生溢出时向所有缓存广播失效。
* $$ Dir_i NB $$ 当发生溢出时，通过置换的方式失效其中一个缓存。
* $$ Dir_i X $$ 保存两个指针，当指针溢出，同样的内存转化为一个组合指针。2bits 表示指针的一个bit位的3个状态：1、0、both。这种方式将组合指针映射到一个指针集合，这样就解决了指针溢出的问题。

##Optimization Methods
__New Proposals__ to reduce memory requirements of directory schemes without significantly compromising performance and communication requirements.

* Coarse Vector Scheme ($$Dir_i CVr$$)
    - i is the number of pointers and r is the size of the region that each bit in the coarse vector represents 
    - The pointer storage memory reverts to a bit vector when pointer overflow
    - Each bit of this bit vector stands for a group of r processors 
* Sparse Directories
    - The total amount of cache memory in a multiprocessor is much less than the total amount of main memory 
    - Replacing an entry of the sparse directory after invalidating all processor caches which that entry points to
    - Replacement policies

对基于目录的方案，其内存占用有两个维度，一个是单条目录信息的内存占用，另一个是
目录的条目数量。针对这两个维度，提出另外两种方案：

- 粗粒度向量(Coarse Vector Scheme)：一个bit代表一个处理器集合，当失效时只失效这个集合对应的处理器。
- 稀疏目录(Sparse Directories)：因为缓存相对于内存非常小，不需要保存所有目录项的信息。根据缓存的思想，只保存最热的目录项，在失效完相应的缓存后将目录项置换出去。

这两种方案在内存开销和通信成本方面比先前的方案有着显著减低。

- - -

##False Sharing vs. Spatial Locality
__False sharing__ occurs when threads on different processors modify different variables that reside on the same cache line. This invalidates the cache line and forces an update, which hurts performance.

![figure-12]({% image_url false-sharing.png %})

多处理器共享一个缓存行，当同时修改不同的变量，就会产生不必要的失效，这极大影响了性能。缓存行的话可以减少读扑空，但是同时会引入更多伪共享，这就是空间局部性和伪共享的矛盾。

###Conclusion
1. To improve the performance of caches, trying to enhance the spatial locality of multiprocessor data is an approach at least as, or even more promising, than to remove false sharing.
2. Data layout optimizations that are programmer-transparent and not restricted to regular codes can be used to reduce the miss rate. 

 Reduce false sharing                   |Improve the spatial locality of data
:---------------------------------------|:---------------------------------------
 Split Scalars                          |Lock Scalars
 Heap allocation                        |Record alignment
 __Record expansion__ (padding) __(+)__ |
 Record alignment                       |

`note`: (+) Leaving it up to the programmer to pad the data structure if so desired.

- 为了提高缓存的性能，增强空间局部性比消除伪共享更有效。因为对于扑空率的影响，空间局部性比伪共享的作用更加显著。
- 对程序员透明的数据布局优化和不限制在常规代码中使用相关技术将有助于减少缓存的扑空。
- 对于程序员来讲，alignment 和 padding 是非常有效的技术来避免伪共享。

- - -

##Related Reference

This presentation is based on lots of papers, books and information on internet. Here are the main reference:

1. "Parallel Computer Architecture A Hardware/Software Approach" by Culler and Singh, published by Morgan Kaufmann, 1997.
2. D. Lenoski et al. "The Directory-Based Cache Coherence Protocol for the DASH Multiprocessor" International Symposium on Computer Architecture 1990.
3. A. Gupta et al. "Reducing Memory and Traffic Requirements for Scalable Directory-Based Cache Coherence Schemes", International Conference on Parallel Processing 1990.
4. J. Torrellas, M. Lam & J. Hennessy "False Sharing and Spatial Locality in Multiprocessor Caches" Transactions on Computers, June 1994.
5. "Computer Architecture: A Quantitative Approach, 4th Edition" by John L. Hennessy and David A. Patterson, 2006.
6. The presentation named "Directory-Based Cache Coherence Protocols" of Portland State University ECE 588/688. \[[link](http://web.cecs.pdx.edu/~alaa/ece588/notes/directory-protocols.pdf)\]

