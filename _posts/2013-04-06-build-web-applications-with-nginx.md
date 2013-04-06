---
layout: post
title: "使用Nginx构建Web应用程序"
description: ""
category: technology
tags: []
---
{% include JB/setup %}

_This is originated from a share of the internal. Almost all the work is based on Openresty of agentzh, and some of the examples are retrieved from the wiki directly._

Build Web applications with Nginx
==========
---

* high-performance
* small memory footprint

__apache__ threaded or process-oriented model.
__nginx__ asynchronous event-driven model (I/O multiplexing)
nginx is a web application framework.

Note:


Apache server utilizes "embedded interpreter" approach. Dynamic content is typically handed off to CGI, FastCGI. And Nginx's ability to efficiently serve static content and deal with high concurrency.

And how to use Nginx to handle dynamic content and to build a web app?
_web server / proxy server / mail proxy server_

---

The Basics of Nginx
----------

###Basic configuration : _nginx.conf_

    #nginx.conf
    worker_processes 4;
    events {
        worker_connections 1024;
    }
    http {
        upstream tornado{
            server localhost:9876;
        }
        ...
        server {
        listen 80;
        server_name www.zhihu.com;
        ...
        location / {
             proxy_pass http://tornado;
        }
    }


Note:
3 hierarchies:http -> server -> location

---

### HTTP request processing phases

The directives are not executed by sequential order

* NGX_HTTP_SERVER_REWRITE_PHASE
* NGX_HTTP_FIND_CONFIG_PHASE(no handler)
* __NGX_HTTP_REWRITE_PHASE__
* NGX_HTTP_POST_REWRITE_PHASE(no handler)
* NGX_HTTP_PREACCESS_PHASE
* __NGX_HTTP_ACCESS_PHASE__
* NGX_HTTP_POST_ACCESS_PHASE(no handler)
* NGX_HTTP_TRY_FILES_PHASE(no handler)
* __NGX_HTTP_CONTENT_PHASE__(only one handler can take effect)
* NGX_HTTP_LOG_PHASE


Note:

* the phase of request URI transformation on virtual server level;
* the phase of configuration location lookup;
* the phase of request URI transformation on location level;
* request URI transformation post-processing phase;
* access restrictions check preprocessing phase;
* access restrictions check phase;
* access restrictions check post-processing phase;
* try_files directive processing phase;
* content generation phase;
* logging phase.

---

###variable

####built-in variables [http://wiki.nginx.org/HttpCoreModule](http://wiki.nginx.org/HttpCoreModulehttp://wiki.nginx.org/HttpCoreModule)

    $content_type
    $args
    $request_method
    $arg_PARAMETER
    $http_HEADER
    $sent_http_HEADER
    $cookie_COOKIE

####self-built variables

    set $tmp $host;
    set $hi hi;
    set $greeting "$hi, $cookie_user";
    set $hill "${hi}ll"

####exmaple

    if ($http_user_agent ~ MSIE) {
        rewrite  ^(.*)$  /msie/$1  break;
    }

    rewrite  ^/users/(.*)$  /show?user=$1?  last;

    if ($request_method = POST ) {
        return 405;
    }

The Nginx configure file notation is a small language.

[If Is Evil - http://wiki.nginx.org/IfIsEvil](http://wiki.nginx.org/IfIsEvil)

---

### subrequest
* modules can perform multiple subrequests and combine the outputs into a single response
* subrequests can perform their own sub-subrequests, and sub-subrequests can initiate sub-sub-subrequests…
* parallel subrequests


Note:

With subrequests, you can return the results of a different URL than what the client originally requested.

It's also possible to issue several subrequests at once without waiting for previous subrequests to finish.

###example

    location /private/ {
        proxy_pass http://tornado;
        auth_request /auth ;
    }
    location /auth {
        internal;
        if ($cookie_user) {
            return 200;
        }
        return 403;
    }
    location / {
        proxy_pass http://tornado;
    }

---

Handle GET request && ngx_echo_module
----------
###hello world

    location = '/hello' {
        set $person $arg_person;
        set_if_empty $person 'anonymous';
        echo "hello, $person";
    }

###unescape url parameters

    location = '/hello' {
        set_unescape_uri $person $arg_person;
        set_if_empty $person anonymous;
        echo "hello, $person";
    }

###issue subrequests

    location /series {
        echo_location /sub1;
        echo_subrequest_async POST /sub2 -b world;
    }
    location /sub1 {
        echo hello;
    }
    location /sub2 {
        echo $echo_request_body;
    }

###series && parallel

    location /series {
        echo_location /sub1;
        echo_subrequest_async POST /sub2 -b world;
    }
    location /parallel {
        echo_reset_timer;
        echo_location_async /sub1;
        echo_subrequest_async POST /sub2 -b world;
        echo "took $echo_timer_elapsed sec for total.";
    }
    location /sub1 {
        echo_sleep 2; # sleeps 2 sec
        echo hello;
    }
    location /sub2 {
        echo_sleep 1; # sleeps 1 sec
        echo $echo_request_body;
    }

####result

    $ time curl http://gentoo1:9991/series
    hello
    world
    took 2.018 sec for total.

    real    0m3.034s
    user    0m0.000s
    sys 0m0.000s

    $ time curl http://gentoo1:9991/parallel
    hello
    world
    took 0.000 sec for total.

    real    0m2.022s
    user    0m0.000s
    sys 0m0.000s


---

ngx_drizzle for MySQl and Drizzle
----------

###non-blocking

    upstream mysql_backend {
        drizzle_server 127.0.0.1:3306 dbname=nginx_test
            password= user=root
            protocol=mysql;

        drizzle_keepalive max=200 overflow=reject;
    }

    location ~ '^/foo/(\d+)$' {
        set $id $1;
        drizzle_query "select * from foo where a=$id";
        drizzle_pass mysql_backend;
        rds_json on;
    }

###cluster hashing

    http {
        upstream A {
           drizzle_server ...;
        }
        upstream B {
           drizzle_server ...;
        }
        upstream C {
            drizzle_server ...;
        }
        upstream_list my_cluster A B C;
        ...
    }

    location ~ '^/name/(.*)' {
        set $name $1;
        set_quote_sql_str $quoted_name $name;
        drizzle_query "select * from name
           where name=$quoted_name";

        set_hashed_upstream $backend my_cluster $name;
        drizzle_pass $backend;

        rds_json on;
    }


---

ngx_postgres for PostgreSQL
----------
Note: pass quickly

---

ngx_srcache && ngx_srcache
----------

###General location response cache based on Nginx subrequests

    location /memc {
        internal;
        set_unescape_uri $memc_key $arg_key;
        set $memc_exptime $arg_exptime;
        memc_pass memc_pass 127.0.0.1:11211;
    }

    location /api {
        set $key "$uri?$args";
        srcache_fetch GET /memc key=$key;
        srcache_store PUT /memc key=$key&exptime=3600;

        # proxy_pass/drizzle_pass/postgres_pass/etc
    }

---

ngx_redis2 for Redis
----------

###multiple pipelined queries

    upstream redis {
         server 127.0.0.1:6379;
        keepalive 1024 single;
    }
    ...
    location / {
        set_unescape_uri $key $arg_key;
        set_unescape_uri $val $arg_val;
        if ($key = '') {
            return 403;
        }
        redis2_query set $key $val;
        redis2_query get $key;
        redis2_pass redis;
    }

---

ngx_lua
----------

###API

* set_by_lua
* set_by_lua_file
* content_by_lua
* content_by_lua_file
* rewrite_by_lua
* rewrite_by_lua_file
* access_by_lua
* access_by_lua_file
* header_filter
* header_filter_by_lua_file


###ngx_auth_request


    location / {
        access_by_lua '
            local res = ngx.location.capture("/auth")

            if res.status == ngx.HTTP_OK then
                return
            end

            if res.status == ngx.HTTP_FORBIDDEN then
                ngx.exit(res.status)
            end

            ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
        ';

        # proxy_pass/fastcgi_pass/postgres_pass/...
    }

###Multiple concurrent subrequests in Lua

    location = /api {
        content_by_lua '
            local res1, res2, res3 =
                ngx.location.capture_multi{
                    {"/memc"}, {"/mysql"}, {"/postgres"}
                }
            ngx.say(res1.body, res2.body, res3.body)
        ';
    }

###accessing upstream services in Lua
    location /access_google {
        content_by_lua '
        local sock = ngx.socket.tcp()
        local ok, err = sock:connect("www.google.com", 80)
        if not ok then
            ngx.say("failed to connect to google: ", err)
            return
        end
        ngx.say("successfully connected to google!")
        sock:close()
     ';}

###High-level Lua libraries
* lua-resty-mysql
* lua-resty-memcached
* lua-resty-redis
* lua-resty-upload

####exmaple of lua-resty-redis
    content_by_lua '
        local redis = require "resty.redis"
        local red = redis:new()
        local ok, err = red:connect("127.0.0.1", 6379)
        if not ok then
            ngx.say("failed to connect: ", err)
            return
        end
        res, err = red:set("dog", "an aniaml")
        if not ok then
            ngx.say("failed to set dog: ", err)
            return
        end
        ngx.say("set result: ", res)
        red:set_keepalive(0, 100)
    ';


##Reference
* [http://openresty.com/](http://openresty.com/)
* [http://blog.martinfjordvald.com/2010/07/nginx-primer/](http://blog.martinfjordvald.com/2010/07/nginx-primer/)
* [http://www.nginxguts.com/2011/01/phases/](http://www.nginxguts.com/2011/01/phases/)
* [http://www.evanmiller.org/nginx-modules-guide-advanced.html](http://www.evanmiller.org/nginx-modules-guide-advanced.html)
* [http://blog.sina.com.cn/s/articlelist\_1834459124\_1\_1.html](http://blog.sina.com.cn/s/articlelist_1834459124_1_1.html)
* [http://www.ruby-forum.com/topic/205063](http://www.ruby-forum.com/topic/205063)
* [http://wiki.nginx.org/HttpEchoModule#echo\_subrequest](http://wiki.nginx.org/HttpEchoModule#echo_subrequest)
