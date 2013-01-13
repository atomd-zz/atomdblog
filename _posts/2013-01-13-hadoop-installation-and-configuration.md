---
layout: post
title: "Hadoop集群的安装和配置"
description: ""
category: 
tags: []
---
{% include JB/setup %}

因为实验式的项目要用到Hadoop，参加了ChinaHadoop办的Hadoop大数据平台的在线培训。用的是YY的平台，第一次用感觉问题不少，尤其是其中的白板功能。前几日和导师吃饭的时候，他说上课是没有效率的，研究生应该以自学为主。我认同，因为学校一些课真的比较水，但我觉得不管上课还是自学都取决于交流的质量。如果真的有富有经验的人愿意传道授业解惑，并且没有交流障碍，无疑会有很大的帮助，也会避免走很多弯路，这样的课是用很大价值的，完全值得300的价格。这里也推荐下这个课:)

在第一讲的时候主要讲到了Hadoop的前世今身和安装配置方法。这里简单记录下：

因为使用YY，所以选择在Windows下使用VMware来管理虚拟机。

 机器角色        | IP             | 机器名 | 用户名 | 配置
:---------------:|:--------------:|:------:|:------:|:-----------------:
 Master + Slave1 | 192.168.32.111 | X001   | hadoop | 内存1G，硬盘20G
 Slave2          | 192.168.32.112 | X002   | hadoop | 内存724M, 硬盘20G
 Slave3          | 192.168.32.113 | X003   | hadoop | 内存724M，硬盘20G

* VMware Workstation 9.0
* ubuntu-12.04.1-desktop-i386.iso

###主要步骤

####创建虚拟机X001

#####配置网络
- 将网卡配置NET的方式。这样虚拟机的网络环境不随宿主机的网络环境变化，而且可以和外网连接。
- 配置IP 192.168.32.11，掩码 255.255.255.0，网关 192.168.32.2, DNS 192.168.32.2。

#####更新软件

    $ sudo apt-get update
    $ sudo apt-get upgrade

#####安装SSH

    $ sudo apt-get install ssh

#####修改配置文件

    $ sudo vim /etc/ssh/ssh_config
    StrictHostKeyChecking no

    $ sudo service ssh restart

#####修改hostname为X001

    $ sudo vi /etc/hostname
    X001

#####修改hosts
    $ vim /etc/hosts

    127.0.0.1   localhost
    127.0.1.1   X001-local
    192.168.1.111   X001
    192.168.1.112   X002
    192.168.1.113   X003

#####下载hadoop和Java
* hadoop: hadoop-1.0.4.tar.gz
* Java JDK: jdk-7u7-linux-i586.tar.gz

#####如果通过ftp上传可以安装vsftpd：
    $ sudo apt-get install vsftpd
    $ sudo vi /etc/vsftpd.conf

    listen=YES
    anonymous_enable=NO
    local_enable=YES
    write_enable=YES
    local_umask=022
    anon_upload_enable=YES
    dirmessage_enable=YES
    use_localtime=YES
    xferlog_enable=YES
    connect_from_port_20=YES
    async_abor_enable=YES
    ascii_upload_enable=YES
    ascii_download_enable=YES
    secure_chroot_dir=/var/run/vsftpd/empty
    pam_service_name=vsftpd
    rsa_cert_file=/etc/ssl/private/vsftpd.pem

    $ sudo service vsftpd restart

####安装Java

#####切换为root用户
    $ sudo su -

#####解压到/usr/java目录下
    $ tar -xvf /usr/java/jdk-7u7-linux-i586.tar.gz

#####设置JAVA环境变量，修改/etc/profile，在文件尾部加入
    $ sudo vim /etc/profile

    # set java env
    export JAVA_HOME=/usr/java/jdk1.7.0_07
    export JRE_HOME=/usr/java/jdk1.7.0_07/jre
    export CLASSPATH=.:$CLASSPATH:$JAVA_HOME/lib:$JRE_HOME/lib
    export PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin

#####测试安装
    $ source /etc/profile
    $ java -version

####安装Hadoop

#####切换为hadoop用户
    $ sudo su hadoop

#####解压在目录/usr/hadoop-1.0.4
    $ tar -xvf /usr/hadoop-1.0.4.tar.gz

#####切换为root用户
    $ sudo su -

#####修改/etc/profile，设置Hadoop环境变量
    $ sudo vim /etc/profile

    # set hadoop env
    export HADOOP_HOME=/usr/hadoop-1.0.4
    export PATH=$PATH:$HADOOP_HOME/bin
    export HADOOP_HOME_WARN_SUPPRESS=1

#####使环境生效
    $ source /etc/profile

####hadoop的基本配置(/usr/hadoop-1.0.4/conf)
    $ vim hadoop-env.sh
    export JAVA_HOME=/usr/java/jdk1.7.0_07

#####修改core-site.xml，tmp.dir不要放在/tmp下
    $ vim core-site.xml

    <configuration>
    <property>
        <name>hadoop.tmp.dir</name>   
        <value>/usr/hadoop-1.0.4/tmp.dir</value>   
        <description>A base for other temporary dirs.</description>
    </property>
    <property>   
        <name>fs.default.name</name>   
        <value>hdfs://192.168.32.111:9000</value>
    </property>
    </configuration>

#####修改 hdfs-site.xml， permision为false是为了开发方便，replication副本数为2（缺省值为3），因为测试环境中一共是3个节点。
    $ vim hdfs-site.xml 

    <configuration>
    <property>
        <name>dfs.replication</name>
        <value>2</value> 
    </property> 
    <property>
        <name>dfs.permissions</name> 
        <value>false</value>
    </property>
    </configuration>

#####修改mapred-site.xml
    $ vim mapred-site.xml 
    <configuration>
    <property>
        <name>mapred.job.tracker</name>
        <value>http://192.168.32.111:9001</value>
    </property>
    </configuration>

#####修改masters和slaves文件
    $ cat masters 
    192.168.32.111

    $ cat slaves 
    192.168.32.111
    192.168.32.112
    192.168.32.113

####通过vmware 克隆出X002和X003

#####按照X001的方式对Ip、 Hostname、Hosts进行修改

#####分配对三个节点配置SSH无密码登陆

    $ ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""
    $ ssh-copy-id hadoop@X001
    $ ssh-copy-id hadoop@X002
    $ ssh-copy-id hadoop@X003



这样就完成3个节点的hadoop的测试环境的搭建

###测试基本功能

####在master机器上，格式化HDFS文件系统
    hadoop@X001:~$ hadoop namenode -format
    ...
    1.0.4/tmp.dir/dfs/name has been successfully formatted.
    ...

####启动Hadoop
    hadoop@X001:~$ start-all.sh

    starting namenode, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-namenode-X001.out
    192.168.32.112: starting datanode, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-datanode-X002.out
    192.168.32.113: starting datanode, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-datanode-X003.out
    192.168.32.111: starting datanode, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-datanode-X001.out
    192.168.32.111: starting secondarynamenode, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-secondarynamenode-X001.out
    starting jobtracker, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-jobtracker-X001.out
    192.168.32.112: starting tasktracker, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-tasktracker-X002.out
    192.168.32.113: starting tasktracker, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-tasktracker-X003.out
    192.168.32.111: starting tasktracker, logging to /usr/hadoop-1.0.4/libexec/../logs/hadoop-hadoop-tasktracker-X001.out

####查看启动进程
    hadoop@X001:~$ jps
    7740 DataNode
    7516 NameNode
    8427 Jps
    8271 TaskTracker
    7956 SecondaryNameNode
    8039 JobTracker

    hadoop@X002:~$ jps
    4722 DataNode
    4960 Jps
    4915 TaskTracker

####通过Web查看节点状态
访问http://192.168.32.111:50030 或 http://192.168.32.111:50070 来查看集群的相关信息


