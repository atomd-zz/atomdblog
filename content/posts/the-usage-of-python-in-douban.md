Title: python在douban的使用
Date: 2013-04-20 21:03
Description: ""
Category: technology
Tags: python
Slug: the-usage-of-python-in-douban
---

内容源于洪强宁的一次分享, 以下是其演讲的一些笔记。

###协同开发环境
* 协同开发环境 mercurial(hg)
* 知识和项目管理 trac
* 交流沟通 IRC **开源协议（如上线通知机器人）**

###前端
* 模板 Mako
* 静态文件处理. 如自动处理静态文件URL和自动js内联
* 预编译系统. @import
* 引入pyScss.

###移动端
* APNS Agent.  **gevent+bottle+APNSWrapper**

###产品开发
* web框架 Quixote v1.2 只使用了url dispatch部分，**Traversal based，非正则匹配，类似目录层级的线性查找，比route based性能好，易于控制，如在某个层级统一对请求拦截、查找**
* 大量使用语言特性. 如decorator，generator（**这里举了个feed合并的例子，见[Python于Web 2.0网站的应用](http://slidesha.re/tVis) page102**), meta(黑魔法)
* OneRing 开源，web技术做桌面应用

###技术支持
* Restful MongoDB Service.   django-piston+sleepy

###QA
* pylint 在代码提交后做静态检查，自制插件SQL inject漏洞检查，XSS漏洞检查等
* onimaru 错误收集系统，统计及展示，基于 django-sentry实现
* release manager 自动打tag，确认测试结果，发送email及irc－bot通知，django实现

###算法
关注性能

* cmy Mysql Client, C API＋python wrapper,只支持select,返回iterator,比MySQLdb在大数据量时性能高一个数量级
* C++ Intergration，C++实现算法（boost python）,python加载和初始化数据来保证灵活

###平台
关注性能

* Online Profiler 性能分析工具，举例提到的是页面渲染的分析工具，包括函数执行时间，SQL数量及时间，memcached访问和时间等，利用了python hotshot模块
* DoubanService thrift RPC, PasteScript实现代码生成和提供服务，客户端负责负责均衡和failover（将[thrift_client](https://github.com/twitter/thrift_client)移植到python）,nagios和munin集成监控
* Dpark 分布式计算框架，将Spark移植到python，基于mesos实现资源调度
* pypcap + dpkt 对mysql抓包，进行分析检查，对slave热备（**这里提到了在他们是一主加一个热备，在现在的数据规模下，slave需要几十分钟才能达到正常水平，这是不是说明虽然不依赖mysql的缓存，但这个缓存也有些作用**）
* DAE Google AppEngine, 内部使用. 提到的技术有virtualenv、gunicorn、gevent。

除了python，还使用C\C++, **go**, **R**, obj-c, java, c#

PS：这次pyCon的多个议题都提到了coroutine, 或许引入协程会是python web开发的未来。
