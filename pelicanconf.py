#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from __future__ import unicode_literals

################################################################################
# General
################################################################################

SITENAME = u'The Other Shore'
AUTHOR = u'atomd'
TAGLINE = u'Programmer • Writer'

TIMEZONE = 'Asia/Hong_Kong'
DEFAULT_LANG = u'en'
DEFAULT_DATE_FORMAT = ('%a, %d %b %y')
DEFAULT_PAGINATION = 5

DISPLAY_PAGES_ON_MENU = True
DELETE_OUTPUT_DIRECTORY = True
SUMMARY_MAX_LENGTH = 40


################################################################################
# Appearance
################################################################################

#TYPOGRIFY = True
THEME = 'themes/svbtle'


################################################################################
# Paths and URLs
################################################################################

SITEURL = ''
RELATIVE_URLS = True

STATIC_PATHS = ['images', 'static', ]
FILES_TO_COPY = (
    ('extra/favicon.ico', 'favicon.ico'),
    ('extra/CNAME', 'CNAME'),
    ('extra/robots.txt', 'robots.txt'),
)
#THEME_STATIC_PATHS = STATIC_PATHS
MARKUP = ('md', 'rst')


#GITHUB_RAW_URL_ROOT = ''

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

FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'

################################################################################
# Plugins
################################################################################
PLUGIN_PATH = 'plugins'
PLUGINS = ['latex',]

################################################################################
# Social
################################################################################

LINKS = ()
SOCIAL = (
    ('github', 'https://github.com/atomd'),
    ('bitbucket', 'https://bitbucket.org/atomd'),
    ('douban', 'http://www.douban.com/people/atomd/'),
)
