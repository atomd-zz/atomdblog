---
layout: post
title: "The Basic of Scalable Cache Coherence"
description: ""
category: tech
tags: []
---
{% include JB/setup %}

###The Role of Cache
1. Reducing the average memory access time
2. Reducing the bandwidth requirement

![figure-1]({% image_url common-memory-hierarchies-found-in-multiprocessors.png %})

- - -

###The Cache Coherence Problem
* Pervasive and performance critical in multiprocessors.
* Each read should return the latest value written to that location.

![figure-2]({% image_url example-cache-coherence-problem.png %})
Write back cache or Write through cache ?   
Write invalidate  or Write update ？

- - -

###Coherency vs. Consistency
Cache coherency and consistency define the action of the processors to maintain coherence. 

* Coherency defines what value is returned on a read
* Consistency defines when it is available

- - -

###Cache Coherence protocols
####Snooping
1. The caches are all accessible via some __broadcast__ medium (a bus or switch)
2. All cache controllers monitor or __snoop on the medium__ to determine whether or not they have a copy of a block that is requested

####Directory Based
1. The sharing status of a block of physical memory is kept in just one location, called the __directory__
2. using __point-to-point messages__ sent between the processors and memories to keep caches consistent

- - -

###Snooping
* Single physical address space with uniform memory access (UMA) times.
* The bus severs an arbitrator for serializing accesses to a shared line.
* All caches see the same sequence of writes.
* The cache coherence traffic creates another limit on the scale and the speed of the processors. 
![figure-3]({% image_url snoopy-cache-coherent-multiprocessor.png %})

- - -

###MESI (Illinois) Protocol
![figure-4]({% image_url state-transition-diagram-for-the-Illinois-MESI-protocol.png %})

####States
* Modified
* Exclusive
* Shared
* Invalid

####Requests by processors
* PrRd
* PrWr

####Actions by bus
* BusRd
* BusRdX
* BusWB

- - -

###Directory Based
* Coherence state maintained in a directory associated with memory
* Requests to a memory block do not need broadcasts
![figure-5]({% image_url a-scalable-multiprocessor-with-directories.png %})

- - -

###Example: DASH
![figure-6]({% image_url block-diagram-of-a-2x2-bash-prototype.png %})

- - -

###The Stanford DASH Prototype
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

- - -

###DASH Directory board
![figure-8]({% image_url directory-board-block-diagram.png %})

- - -

###DASH Coherence Protocol
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

- - -

###Read Requests
* Initiated by CPU load instruction
* If address is in L1 cache, L1 supplies data – otherwise, fill request sent to L2
* If address is in L2, L2 supplies data – otherwise, read request sent on bus
* If address is in the cache of another processor in the cluster or in the RAC, that cache responds
    - Shared: data transferred over the bus to requester
    - Dirty: data transferred over bus to requester, RAC takes ownership of cache line
* If address not in local cluster, processor retries bus operation, and request is sent to home cluster, RAC entry is allocated
* If the block is in an uncached-remote or shared-remote state the directory controller sends the data over the reply network to the requesting cluster. 
* Requests to remote memory with directory in dirty-remote state explained in paper 2 figure 4
![figure-9]({% image_url flow-of-Read-Request-to-remote-memory-with-directory-in-dirty-remote-state.png %})

- - -

###Read-Exclusive Requests
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
* Requests to remote nodes in shared-remote state explained in paper 2 figure 5
* Requests to remote nodes in dirty-remote state explained in the next.
![figure-11]({% image_url flow-of-read-exclusive-request-to-remote-memory-with-directory-in-shared-remote-state.png %})
![figure-10]({% image_url flow-of-read-exclusive-request-to-remote-memory-with-directory-in-dirty-remote-state.png %})

- - -

###Other Implementation Details
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

###Directory Schemes
* Full Bit Vector Scheme (need $$ P^2 * M / B $$ bits)
* Cache-Based Linked List Schemes
* Limited Pointer Schemes
    - log2P bits per pointer, need $$ (i \times log_2^P) \times (P \times M/B) $$ bits
    - How to deal with the pointer overflow?
        * Limited Pointers with Broadcast Scheme ($$ Dir_i B $$)
        * Limited Pointers without Broadcast Scheme ($$ Dir_i NB $$)
        * Limited Pointers superset Scheme ($$ Dir_i X $$)

###Optimization Methods
