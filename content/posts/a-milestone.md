Title: 在Linode上部署python web项目
Date: 2013-05-2 20:23
Description: ""
Category: technology
Tags: linode, deployment
Slug: a-milestone


## Linode Statistics
![figure-1](|filename|/images/a-milestone/linode2.png)

## Google Realtime Analysis
![figure-2](|filename|/images/a-milestone/top_realtime.png)

## 服务器上的配置

服务采用 Flask (gevent patching) + gunicorn + MySQL.

服务器按照 Linode 的文档进行配置，尤其是这两篇：
- [Linux Security Basics](https://library.linode.com/security/basics)
- [Hosting a Website](https://library.linode.com/hosting-website)

Linode文档真心很全面，虽然都很基础，但目睹了郝哥轻松拖了某小公司的数据库，发现小处着眼，方能解决大问题。怎么被脱库的呢，那个公司是数据库可公网访问，Root 登录，密码123456，看了我都直呼，Oh，My God!

最后附上 @hellosa 给我发的优化配置:

    # /etc/sysctl.conf :
    # =================================================

    net.ipv4.ip_forward = 0

    ######## important #####################

    net.netfilter.nf_conntrack_tcp_timeout_established = 3600
    net.ipv4.tcp_timestamps = 0

    ########################################

    net.ipv4.conf.all.send_redirects = 1
    net.ipv4.conf.default.send_redirects = 1
    net.ipv4.conf.eth0.send_redirects = 1

    net.ipv4.conf.default.rp_filter = 0
    net.ipv4.conf.default.accept_source_route = 0

    kernel.printk = 4 4 1 7
    kernel.sysrq = 0
    kernel.core_uses_pid = 1
    kernel.panic = 10
    kernel.msgmnb = 65536
    kernel.msgmax = 65536
    kernel.shmmax = 68719476736
    kernel.shmall = 4294967296


    net.ipv4.tcp_fin_timeout = 30
    net.ipv4.tcp_tw_recycle = 1
    net.ipv4.tcp_tw_reuse = 1

    net.core.rmem_max = 16777216
    net.core.rmem_default = 8388608
    net.ipv4.tcp_rmem = 4096 65535 16777216

    net.core.wmem_max = 33554432
    net.core.wmem_default = 8388608
    net.ipv4.tcp_wmem = 4096 65535 33554432

    net.ipv4.tcp_mem = 786432 2097152 3145728

    net.core.optmem_max = 40960
    net.core.netdev_max_backlog = 262144
    net.core.somaxconn = 262144

    net.ipv4.tcp_syncookies = 1
    net.ipv4.tcp_max_orphans = 3276800
    net.ipv4.tcp_max_syn_backlog = 262144
    net.ipv4.tcp_synack_retries = 1
    net.ipv4.tcp_syn_retries = 1

    net.ipv4.tcp_orphan_retries = 0
    net.ipv4.ip_local_port_range = 1024  65535
    net.ipv4.tcp_window_scaling = 0
    net.ipv4.tcp_keepalive_time = 1800

    net.ipv4.conf.all.rp_filter = 0
    net.ipv4.conf.default.rp_filter = 0
    net.ipv4.conf.lo.rp_filter = 0
    net.ipv4.conf.eth0.rp_filter = 0
    net.ipv4.conf.eth1.rp_filter = 0
    net.ipv4.conf.em1.rp_filter = 0
    net.ipv4.conf.em2.rp_filter = 0

    net.ipv4.ip_default_ttl = 255

    fs.file-max = 655350

我们之前开玩笑说，不会连本科娱乐的作品也超越不了吧。这周归档文件时，我就把相关记录翻出来了。虽然东西API都很简单，但是从流量和并发来看，我在单实例的Linode512上完成的还是不错的。
