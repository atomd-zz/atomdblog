---
layout: post
title: "MySQL的复制与高可用性"
description: ""
category: technology
tags: []
---
{% include JB/setup %}

#MySQL Replication and high Availability

---

#Replicaiton Implementation

##Three thread
- Binlog dump thread
- Slave I/O thread
- Slave SQL thread

###How MySQL replicaiton works
![p-1]({% image_url Replicaiton.png %})

##Two ways
* asynchronous
* semi-synchronous(5.5+)

---

##Maatkit
* mk-table-checksum : Perform an online replication consistency check, or checksum MySQL tables efficiently on one or many servers
* mk-archiver : Archive rows from a MySQL table into another table or a file
* mk-audit : Analyze, summarize and report on MySQL config, schema and operation
* mk-duplicate-key-checker : Find duplicate keys and foreign keys on MySQL tables
* mk-deadlock-logger : Extract and log MySQL deadlock information
* mk-visual-explain : Format EXPLAIN output as a tree
* mk-parallel-dump : Dump sets of MySQL tables in parallel
* mk-parallel-restore : Load files into MySQL in parallel
* mk-query-digest Parses logs and more. Analyze, transform, filter, review and report on queries

---

#Replication Configuration

##Step 1 Preparation work

###Setting the Configuration

    [mysqld]
    log-bin=<path for binary log>
    server-id=<different id>
    binlog-do-db=<database name>
    binlog-ignore-db=<database name>

###Creating a User for Replication

    mysql> CREATE USER 'repl'@'%.mydomain.com' IDENTIFIED BY 'slavepass';
    mysql> GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%.mydomain.com';

##Step 2 Get a snapshot of the master
* Database cold backup
* Software with Snapshot feature(ZFS, LVM ...)
* mysqldump/XtraBackup

---

#Replication Configuration

###mysqldump

    mysql> FLUSH TABLES WITH READ LOCK;
    mysql> SHOW MASTER STATUS;
    +------------------+----------+--------------+------------------+
    | File             | Position | Binlog_Do_DB | Binlog_Ignore_DB |
    +------------------+----------+--------------+------------------+
    | mysql-bin.000008 | 88       | test         | manual, mysql    |
    +------------------+----------+--------------+------------------+
    shell> mysqldump -master-data -uatomd -p test > db.dump
    mysql> UNLOCK TABLES;

##Step 3 Restore the snapshot to slave

    shell> mysql -uatomd -p -Dtest < db.dump

##Step 4 Configure and start the slave

    mysql> change master to master_host='masterhost',
    -> master_user='repl',
    -> master_password='slavepass',
    -> master_log_file='mysql-bin.000008',
    -> master_log_pos=88;
    mysql> start slave;

---

#Replication Solutions

---

##Master-Slaves
![p-2]({% image_url Master-Slaves.png %})

---

#Replication Solutions

##Dual-Master
![p-3]({% image_url Dual-Master.png %})

##configuration for preventing key collisions

    auto-increment-increment=<number>
    auto-increment-offset=<number>

---

#Replication Solutions

##Master-Slaves-Slaves
![p-4]({% image_url Master-Slaves-Slaves.png %})

##configuration for chaining replication servers

    log-slave-update

---

#Replication Solutions

##Master-Slaves-Slaves && Dual-Master
![p-5]({% image_url Master-Slaves-Slaves-and-Dual-Master.png %})

---

#High Availability Definition
* Recovery time (a minimum of down-time)
* Data availability (tolerate data loss or not)

##what heartbeat does
![p-6]({% image_url ha_pic.gif %})

---

#HA Solutions

---

#MySQL with DRBD
* Network RAID 1
* Active / Passive (hot vs cold)
* complexity

##consistency!
![[p-7]({% image_url drdb.gif %})

---

#MySQL Cluster NDB
__MySQL Cluster__ is a technology that enables clustering of in-memory databases in a shared-nothing system.

##components
![p-8]({% image_url cluster-components.png %})

##In MySQL Cluster 7.0
* 4 Node Cluster, 251,000 Transactions/min. 2 Node Cluster, 143,000 Transactions/min

---

#Galera Cluster
__MySQL/Galera__ is synchronous multi-master cluster for MySQL/InnoDB database.

##features
* Synchronous replication
* Active-active multi-master topology
* Read and write to any cluster node
* Automatic membership control, failed nodes drop from the cluster
* Automatic node joining
* True parallel replication, on row level
* Direct client connections, native MySQL look & feel

![p-9]({% image_url galera.png %})

---

#MySQL Replication

##Difficulties
Asynchronous or Semisynchronous - Consistency!

##For example, Master-Slaves-Slaves
![p-10]({% image_url mha-problem.png %})


---

#MySQL Replication

## MHA(MySQL Master HA)
![p-11]({% image_url mha_recovery_procedure.png %})

##others
* MMM(Multi-Master Replication Manager)
* PRM(Percona Replication Manager)


---

# MHA(MySQL Master HA)
![p-12]({% image_url components_of_mha.png %})

* SSH public key authentication
* Preserve relay logs and purge regularly
* master\_ip\_failover\_script, shutdown\_script, report\_script, secondary\_check\_script

---

#MySQL Proxy
MySQL Proxy is a simple program that sits between your client and MySQL server(s) that can monitor, analyze or transform their communication.

* load balancing
* failover
* query analysis
* query filtering and modification
* R/W Splitting
* Connection Pool
* ...

##Using Lua Script
* connect\_server, read\_handshake
* read\_auth, read\_auth\_result
* read\_query, read\_query\_result
* disconnect\_client


---

#MySQL Proxy

![p-13]({% image_url proxy.png %})

---


##FAQ:How much latency does a proxy add to a connection?
In the range of 400 microseconds per request.

    mysqlslap -a -c50 -einnodb --number-int-cols=4 --number-char-cols=35 --number-of-queries=1000

###proxy -> mysql
number of seconds to run all queries: 37 seconds
4 cores, 4 event-threads, 170%CPU, 0.7%MEM, 175.7 M

###mysql
number of seconds to run all queries: 30 seconds

##problems
* lua scripts are difficult to write and debug
* the interface is not so flexible
* performance

---

#Vitess
It does a lot of optimization on the fly, it rewrites queries and acts as a proxy. Currently it serves every YouTube database request. It's RPC based.

##Motivation and vision

* Sessionless connections
* ACID (Atomicity)
* ACID (Consistency)
* Buffer cache vs. row cache
