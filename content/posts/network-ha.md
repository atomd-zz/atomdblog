Title: 网络资源的高可用技术使用以及分析
Date: 2013-08-25 19:03
Category: technology
Tags: ha
Slug: network-ha

因为项目的原因，我决定开始一个专题来分析网络层面的高可用技术(这个划分方式并不准确），主要围绕相关项目使用方式和技术架构。

### 项目
- LVS
- Keepalived
- Heartbeat
- Pacemaker
- Tcpcopy

### 技术
- CARP
- VRPR

*未完待续*

## Keepalived
使用Keepalived，其使用VRRP协议来保证高可用或热备，用来防止单点故障的发生。

![IP](http://www.keepalived.org/images/Software%20Design.gif)

Keepalived也是模块化设计，不同模块复杂不同的功能：

* core：是keepalived的核心，复杂主进程的启动和维护，全局配置文件的加载解析等
* check：负责healthchecker(健康检查)，包括了各种健康检查方式，以及对应的配置的解析包括LVS的配置解析
* vrrp：VRRPD子进程，VRRPD子进程就是来实现VRRP协议的
* libipfwc/libipvs：配置LVS会用到

### Keepalived 安装

```bash
$ wget http://www.keepalived.org/software/keepalived-1.2.7.tar.gz
$ tar -zxvf keepalived-1.2.7.tar.gz
$ cd keepalived-1.2.2
$ ./configure --prefix=/usr/local/keepalived
$ make && make install
# 文件拷贝
$ cp /usr/local/keepalived/etc/rc.d/init.d/keepalived /etc/init.d/keepalived
$ cp /usr/local/keepalived/sbin/keepalived /usr/sbin/
$ cp /usr/local/keepalived/etc/sysconfig/keepalived /etc/sysconfig/
$ mkdir -p /etc/keepalived/
$ cp /usr/local/keepalived/etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf 
```

### 主要配置
#### 两台机器IP配置
* 10.0.3.2 (Master：eth0)
* 10.0.3.3 (Backup：eth0)
#### Master 配置

``` text
! Configuration File for keepalived

vrrp_script chk_tcp {
    script "bash -c '</dev/tcp/0.0.0.0/8889'" # connects and exits
    interval 1 # check every 1 second
    weight -10 # default prio: -2 if connect fails
    fall 2
    rise 2
}

global_defs {
   notification_email {
     dwb319@gmail.com
   }
   notification_email_from mail@lab.org
   ! smtp_server 192.168.200.1
   ! smtp_connect_timeout 30
   router_id LVS_DEVEL
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 101
    advert_int 1

    authentication {
        auth_type PASS
        auth_pass 1111
    }
    track_script {
        chk_tcp
    }
    virtual_ipaddress {
        10.0.3.100
    }
}
```
#### Backup 配置

``` text
! Configuration File for keepalived

vrrp_script chk_tcp {
    script "bash -c '</dev/tcp/10.0.3.3/8889'" # connects and exits
    interval 1 # check every 1 second
    weight -10 # default prio: -2 if connect fails
    fall 1
    rise 2
}

global_defs {
   notification_email {
     dwb319@gmail.com
   }
   notification_email_from mail@lab.com
   ! smtp_server 192.168.200.1
   ! smtp_connect_timeout 30
   router_id LVS_DEVEL
}

vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    track_script {
        chk_tcp
    }
    virtual_ipaddress {
        10.0.3.100
    }
}
```
#### 使用
* /etc/init.d/keepalived start | restart | stop
* 通过 ip a 查看virtual ip
* 日志信息在/var/log/message
