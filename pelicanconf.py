#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

SITENAME = u'The Other Shore'
AUTHOR = u'atomd'
TAGLINE = u'Programmer • Writer'
TIMEZONE = 'Asia/Hong_Kong'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
RELATIVE_URLS = True

DEFAULT_PAGINATION = 5
RECENT_ARTICLES_COUNT = 20

ARTICLE_URL = 'posts/{category}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{category}/{slug}/index.html'

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

AUTHOR_URL = 'author/{slug}/'
AUTHOR_SAVE_AS = 'author/{slug}/index.html'

CATEGORY_URL = 'category/{slug}/'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'

TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = 'tag/{slug}/index.html'
# Blogroll

LINKS = ()
# Social widget

SOCIAL = (
    ('github', 'https://github.com/atomd'),
    ('bitbucket', 'https://bitbucket.org/atomd'),
    ('douban', 'http://www.douban.com/people/atomd/'),
)

# built-texts -> fresh -> pelican-cait -> monospace -> svbtle -> sundown -> lannisport
THEME = "pelican-themes/elegant"  # Good

PLUGIN_PATH = 'pelican-plugins'
PLUGINS = ['latex', ]

STATIC_PATHS = ['images', 'static', 'extras']

EXTRA_PATH_METADATA = {
    'extras/CNAME': {'path': 'CNAME'},
    'extras/robots.txt': {'path': 'robots.txt'},
    'extras/favicon.ico': {'path': 'favicon.ico'},
}
