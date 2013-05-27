title: MHA 的使用方式
Date: 2013-04-11 20:03
Category: technology
Tags: mysql, mha, ha
Slug: the-usage-of-mha

##安装
MHA由Node和Manager模块组成，Node运行在每一台MySQL服务器上。

###安装 MHA Node
[https://github.com/yoshinorim/mha4mysql-node](https://github.com/yoshinorim/mha4mysql-node)

__所以相关服务器都需要部署Node模块__

####依赖
* DBD::mysql

####Ubuntu/Debian

    :::bash
    ## If you have not installed DBD::mysql, install it like below, or install from source.
    $ apt-get install libdbd-mysql-perl

    ## Get MHA Node deb package from "Downloads" section.
    ## http://code.google.com/p/mysql-master-ha/downloads/list
    $ dpkg -i mha4mysql-node_X.Y_all.deb

####source.

    :::bash
    ## Install DBD::mysql if not installed
    $ tar -zxf mha4mysql-node-X.Y.tar.gz
    $ perl Makefile.PL
    $ make
    $ sudo make install

###安装 MHA Manage

__监控管理模块__

####依赖
* MHA Node package
* DBD::mysql
* Config::Tiny
* Log::Dispatch
* Parallel::ForkManager
* Time::HiRes (included from Perl v5.7.3)

####Ubuntu/Debian

    :::bash
    ## Install dependent Perl modules
    $ apt-get install libdbd-mysql-perl
    $ apt-get install libconfig-tiny-perl
    $ apt-get install liblog-dispatch-perl
    $ apt-get install libparallel-forkmanager-perl

    ## Install MHA Node, since MHA Manager uses some modules provided by MHA Node.
    $ dpkg -i mha4mysql-node_X.Y_all.deb

    ## Finally you can install MHA Manager
    $ http://code.google.com/p/mysql-master-ha/downloads/list
    $ dpkg -i mha4mysql-manager_X.Y_all.deb

####source.

    :::bash
    ## Install dependent Perl modules
    # MHA Node (See above)
    # Config::Tiny
    $ perl -MCPAN -e "install Config::Tiny"
    # Log::Dispatch
    $ perl -MCPAN -e "install Log::Dispatch"
    # Parallel::ForkManager
    $ perl -MCPAN -e "install Parallel::ForkManager"
    ## Installing MHA Manager
    $ tar -zxf mha4mysql-manager-X.Y.tar.gz
    $ perl Makefile.PL
    $ make
    $ sudo make install

##需要和限制
* SSH public key authentication
* Linux only
* Single writable master and multiple slaves or read-only masters
* MySQL version 5.0 or later, Use mysqlbinlog 5.1+ for MySQL 5.1+
* log-bin must be enabled on candidate masters
* Binary log and relay log filtering rules must be same on all servers(binlog-do-db, replicate-ignore-db, etc)
* Replication user must exist on candidate masters
* Preserve relay logs and purge regularly
* Do not use LOAD DATA INFILE with Statement Based Binary Logging（SET sql_log_bin=0; LOAD DATA … ; SET sql_log_bin=1; is more recommended approach）


###Note：
* 因为MySQL集群中需要做到ssh无验证互访，所以对账户权限做到最小配置，包括访问MySQL目录下的相关文件，以及MHA中脚本上的命令执行权限。
* 需要禁用自动清除relog log，改为手动定期，MHA提供了purge_relay_logs脚本并配合crontab使用。


##使用

###复制环境
MHA自己不建立MySQL集群的复制环境，而是自己直接运行在已经存在的复制环境之中

###配置
配置分为全局配置和程序配置，它们之间是继承的关系，通常我们只需要程序配置，比如：

    :::ini
    [server default]
    user=root
    password=pwd

    repl_user=replication
    repl_password=slave

    ping_interval=1
    latest_priority=0
    ignore_fail=1
    ssh_user=duanwenbo

    master_pid_file=/home/duanwenbo/master_pid.pid
    remote_workdir=/home/duanwenbo/m
    manager_workdir=/home/duanwenbo/m

    init_conf_load_script=""
    shutdown_script=""
    master_ip_failover_script="/home/duanwenbo/mha4mysql-manager/samples/scripts/master_ip_failover"
    master_ip_online_change_script=""
    report_script=""
    log_level=debug

    [server1]
    hostname=gentoo2


    [server2]
    hostname=gentoo3
    candidate_master=1

    [server3]
    hostname=gentoo8
    no_master=1

    [server4]
    hostname=gentoo7

####比较容易忽略的参数
* candidate_master，由更高的优先级成为master
* no_master,  永远不会成为master
* ignore_fail, MHA Manager不会启动如果有任意一台机子出现，这个参数可以指定忽略一台机子的错误
* latest_priority，用于完全控制服务器的优先级顺序
* ping_interval，如果连续丢失3个ping_interval，则认为master宕机了
* ping_type，ping_type=SELECT(default, "SELECT 1") or ping_type=CONNECT


更多的参数见[http://code.google.com/p/mysql-master-ha/wiki/Parameters#Parameters](http://code.google.com/p/mysql-master-ha/wiki/Parameters#Parameters)

###检查SSH连接

    :::bash
    # masterha_check_ssh --conf=/etc/app1.cnf

    Sat May 14 14:42:19 2011 - [warn] Global configuration file /etc/masterha_default.cnf not found. Skipping.
    Sat May 14 14:42:19 2011 - [info] Reading application default configurations from /etc/app1.cnf..
    Sat May 14 14:42:19 2011 - [info] Reading server configurations from /etc/app1.cnf..
    Sat May 14 14:42:19 2011 - [info] Starting SSH connection tests..
    Sat May 14 14:42:19 2011 - [debug]  Connecting via SSH from root@host1(192.168.0.1) to root@host2(192.168.0.2)..
    Sat May 14 14:42:20 2011 - [debug]   ok.
    Sat May 14 14:42:20 2011 - [debug]  Connecting via SSH from root@host1(192.168.0.1) to root@host3(192.168.0.3)..
    Sat May 14 14:42:20 2011 - [debug]   ok.
    Sat May 14 14:42:21 2011 - [debug]  Connecting via SSH from root@host2(192.168.0.2) to root@host1(192.168.0.1)..
    Sat May 14 14:42:21 2011 - [debug]   ok.
    Sat May 14 14:42:21 2011 - [debug]  Connecting via SSH from root@host2(192.168.0.2) to root@host3(192.168.0.3)..
    Sat May 14 14:42:21 2011 - [debug]   ok.
    Sat May 14 14:42:22 2011 - [debug]  Connecting via SSH from root@host3(192.168.0.3) to root@host1(192.168.0.1)..
    Sat May 14 14:42:22 2011 - [debug]   ok.
    Sat May 14 14:42:22 2011 - [debug]  Connecting via SSH from root@host3(192.168.0.3) to root@host2(192.168.0.2)..
    Sat May 14 14:42:22 2011 - [debug]   ok.
    Sat May 14 14:42:22 2011 - [info] All SSH connection tests passed successfully.


###检查复制配置

    :::bash
    manager_host$ masterha_check_repl --conf=/etc/app1.cnf
    ...
    MySQL Replication Health is OK.

###启动Manager

    :::bash
    manager_host$ masterha_manager --conf=/etc/app1.cnf
    ....
    Sat May 14 15:58:29 2011 - [info] Connecting to the master host1(192.168.0.1:3306) and sleeping until it doesn't respond..

####后台执行, Set nohup, and make sure that masterha_manager does not read/write from/to STDIN, STDOUT and STDERR.

    :::bash
    manager_host$ nohup masterha_manager --conf=/etc/app1.cnf < /dev/null > /var/log/masterha/app1/app1.log 2>&1 &

####Running MHA Manager from daemontools
see [http://code.google.com/p/mysql-master-ha/wiki/Runnning_Background#Running_MHA_Manager_from_daemontools](http://code.google.com/p/mysql-master-ha/wiki/Runnning_Background#Running_MHA_Manager_from_daemontools)

####特定参数
* __last_failover_minute=(minutes)__
If the previous failover was done too recently (8 hours by default), MHA Manager does not do failover because it is highly likely that problems can not be solved by just doing failover.
* __ignore_last_failover__, MHA continues failover regardless of the last failover status.
* __wait_on_failover_error=(seconds)__, it is pretty reasonable for waiting for some time on errors before restarting monitoring again.
* __remove_dead_master_conf__, when this option is set, if failover finishes successfully, MHA Manager automatically removes the section of the dead master from the configuration file.


###检查运行状态

#### masterha_check_status command is useful to check current MHA Manager status.

    :::bash
    manager_host$ masterha_check_status --conf=/etc/app1.cnf
    app1 (pid:5057) is running(0:PING_OK), master:host1

####If manager stops or configuration file is invalid, the following error will be returned.

    :::bash
    manager_host$ masterha_check_status --conf=/etc/app1.cnf
    app1 is stopped(1:NOT_RUNNING).

###停止

    :::bash
    manager_host$ masterha_stop --conf=/etc/app1.cnf
    Stopped app1 successfully.



##脚本


###[purge_relay_logs script](http://code.google.com/p/mysql-master-ha/wiki/Requirements#purge_relay_logs_script)
* --user
* --password
* --host
* --port
* --workdir(Tentative directory where hard linked relay logs are created and removed)
* --disable_relay_log_purge

####Schedule to run purge_relay_logs script

    :::bash
    [app@slave_host1]$ cat /etc/cron.d/purge_relay_logs
    # purge relay logs at 5am
    0 5 * * * app /usr/bin/purge_relay_logs --user=root --password=PASSWORD --disable_relay_log_purge >> /var/log/masterha/purge_relay_logs.log 2>&1

###[master_ip_failover_script](http://code.google.com/p/mysql-master-ha/wiki/Parameters#master_ip_failover_script)
在Master宕机了后，failover调用的脚本。

####Checking phase 相关参数
- --command=status
- --ssh_user=(current master's ssh username)
- --orig_master_host=(current master's hostname)
- --orig_master_ip=(current master's ip address)
- --orig_master_port=(current master's port number)

####Current master shutdown phase 相关参数
- --command=stop or stopssh
- --ssh_user=(dead master's ssh username, if reachable via ssh)
- --orig_master_host=(current(dead) master's hostname)
- --orig_master_ip=(current(dead) master's ip address)
- --orig_master_port=(current(dead) master's port number)

####New master activation phase 相关参数
- --command=start
- --ssh_user=(new master's ssh username)
- --orig_master_host=(dead master's hostname)
- --orig_master_ip=(dead master's ip address)
- --orig_master_port=(dead master's port number)
- --new_master_host=(new master's hostname)
- --new_master_ip=(new master's ip address)
- --new_master_port(new master's port number)

####return
 If the script exits with return code 0 or 10, MHA Manager continues operations. If the script exits with return code other than 0 or 10, MHA Manager aborts and it won't continue failover.

####example
[https://github.com/yoshinorim/mha4mysql-manager/blob/master/samples/scripts/master_ip_failover](https://github.com/yoshinorim/mha4mysql-manager/blob/master/samples/scripts/master_ip_failover)

###[shutdown_script](http://code.google.com/p/mysql-master-ha/wiki/Parameters#shutdown_script)
Master不可用后，用于关闭服务的脚本。

####SSH is reachable  相关参数

- --command=stopssh
- --ssh_user=(ssh username so that you can connect to the master)
- --host=(master's hostname)
- --ip=(master's ip address)
- --port=(master's port number)
- --pid_file=(master's pid file)

####the master is not reachable via SSH  相关参数

- --command=stop
- --host=(master's hostname)
- --ip=(master's ip address)

####example
[https://github.com/yoshinorim/mha4mysql-manager/blob/master/samples/scripts/power_manager](https://github.com/yoshinorim/mha4mysql-manager/blob/master/samples/scripts/power_manager)

###[report_script](http://code.google.com/p/mysql-master-ha/wiki/Parameters#report_script)

###用于告警的script

####相关参数
- --orig_master_host=(dead master's hostname)
- --new_master_host=(new master's hostname)
- --new_slave_hosts=(new slaves' hostnames, delimited by commas)
- --subject=(mail subject)
- --body=(body)

####example
[https://github.com/yoshinorim/mha4mysql-manager/blob/master/samples/scripts/send_report](https://github.com/yoshinorim/mha4mysql-manager/blob/master/samples/scripts/send_report)

###[master_ip_online_change_script](http://code.google.com/p/mysql-master-ha/wiki/Parameters#master_ip_online_change_script)
用于master的动态更换


###[secondary_check_script](http://code.google.com/p/mysql-master-ha/wiki/Parameters#secondary_check_script)

####使用两个或两个以上的网络路由来检查网络的可用性

    :::ini
    secondary_check_script = masterha_secondary_check -s remote_host1 -s remote_host2

PS:已经包括了内置脚本，也可根据自己的需求来扩展


###[init_conf_load_script](http://code.google.com/p/mysql-master-ha/wiki/Parameters#init_conf_load_script)
当不想配置文件出现一些纯文本，比如密码。这个脚本可以用于覆盖全局配置文件。
