from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'browser.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^compare/', include('compare.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
