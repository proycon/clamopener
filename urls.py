from django import VERSION
#from django.views.generic.simple import direct_to_template
from clamopener import settings
import clamopener.clamindex.views
import clamopener.clamusers.views

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

import django.views.static
if VERSION[0] >= 2 or VERSION[1] >= 8: #Django 1.8 and higher
    from django.conf.urls import url, include
    from django.conf.urls.static import static
elif VERSION[1] >= 6: #Django 1.6
    from django.conf.urls import patterns, url, include
    from django.conf.urls.static import static
else:
    from django.conf.urls.defaults import *

urlpatterns = [
    # Example:
    url('^/?$', clamopener.clamindex.views.index ),
    url('^register/?$', clamopener.clamusers.views.register ),
    url('^activate/([0-9]+)/?$', clamopener.clamusers.views.activate ),
    url('^changepw/([0-9]+)/?$', clamopener.clamusers.views.changepw ),
    url('^resetpw/?$', clamopener.clamusers.views.resetpw ),
    url('^report/?$', clamopener.clamusers.views.report ),
    url('^userlist/?$', clamopener.clamusers.views.userlist ),
    url(r'^style/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT}),
]

if VERSION[0] == 1 and VERSION[1] < 8: #Django <1.8
    urlpatterns = patterns('',*urlpatterns)


