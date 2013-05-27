Title: 一些 Git 的小技巧
Date: 2013-03-10 19:03
Category: technology
Tags: git, tips
Slug: git-tips

如果将多个Commit合并成一个，

    :::bash
    $ git reset --soft HEAD^1
    $ git commit --amend
