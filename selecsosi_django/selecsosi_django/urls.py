from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
     url(r'^admin/', include(admin.site.urls)),
     url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
     #url(r'^gps/', include('gps.urls')),
     #url(r'^zoro/', include('zoro.urls')),
     #url(r'^bills/', include('bills.urls')),
     #url(r'^drc/', include('drc.urls')),
     url(r'^$', include('web.urls')),
)
