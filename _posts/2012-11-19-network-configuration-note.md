---
layout: post
title: "Network Configuration Note"
description: "Some note about network configuration."
category: technology
tags: [network, configuration]
---
{% include JB/setup %}

##网桥基本配置
在eth0上开启promisc混杂模式，建立网桥br-100后设置ip，并将eth0桥接到br-100上。

配置如下，其中一些参数的含义详见: <http://linux.die.net/man/8/brctl>。

{% highlight text %}

auto eth0
iface eth0 inet manual
    up ifconfig $IFACE 0.0.0.0 up
    up ip link set $IFACE promisc on
    down ip link set $IFACE promisc off
    down ifconfig $IFACE down

auto br-100
iface br-100 inet static
    address 192.168.5.91
    netmask 255.255.255.0
    network 192.168.5.0
    broadcast 192.168.5.255
    gateway 192.168.5.1
    bridge_ports eth0
    bridge_fd 0
    bridge_stp off
    # bridge_hello 2
    # bridge_maxage 12

{% endhighlight %}

#### bridge\_stp
> The Spanning Tree Protocol (STP) is used to allow multiple bridges
> to work together. Each bridge communicates with other bridges to
> discover how they are interconnected. This information is then used
> to eliminate cycles, and provide optimal routing of packets. 
> STP also provides fault tolerance, because it will recompute the
> topology if a bridge or port fails.

#### bridge\_fd
> This is the forwarding delay for interfaces joining the bridge.


##双网卡配置

`注意`：这种配置方法是存在问题的，其基本原则在于**不应该设定同一网段的不同IP在同一主机上**, 其原因见<http://vbird.dic.ksu.edu.tw/linux_server/0230router.php#routing_double>。

这里不是为了增加主机的网络流量，而是测试下双网卡的工作模式，因为只有一个网关，也就只有采用这个方式了。分两个IP分给两个网卡接口：192.168.50.91、192.168.11.9，一个网关192.168.5.1。配置如下：

{% highlight text %}

auto eth0
iface eth0 inet static
    address 192.168.50.91
    netmask 255.255.0.0
    gateway 192.168.5.1

auto eth1
iface eth1 inet static
    address 192.168.11.91
    netmask 255.255.0.0

{% endhighlight %}

之前的配置出现了其中一个错误:

> RTNETLINK answers: File exists   
> Failed to bring up eth1.

其出现的原因在于eth0、eth1都配置了相同的gateway，导致会出现默认路由规则绑定到了两个接口上，因为冲突而失败。

这种方式有潜在的问题，尽管可以用不同的IP来通过不同的网络接口访问主机，但是主机回复内容都是从一个网络接口出去的。我们可以通过 **route -n** 来查看路由规则:

{% highlight bash %}

Destination  Gateway      Genmask      Flags  Metric Use Iface
0.0.0.0      192.168.5.1  0.0.0.0      UG     100    0 eth0
192.168.0.0  0.0.0.0      255.255.0.0  U      0      0 eth0
192.168.0.0  0.0.0.0      255.255.0.0  U      0      0 eth1

{% endhighlight %}

根据路由规则和优先级，可以看出所有数据包都是eth0直接广播出去，而无需经过eth1。**这样会造成负载均衡、防火墙无法正确配置，甚至会发生数据包传递错误**，这也是鸟哥说的『重复路由问题』。

btw, @hellosa 说 bond 技术(双网卡绑定) 可以解决充分利用双网卡的问题，这是另外的话题，我等得空来看下相关的配置方法。

