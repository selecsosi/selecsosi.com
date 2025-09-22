from django.conf.urls import patterns, include, url


urlpatterns = patterns('web.views',
   # Examples:
   # url(r'^selecsosi_django/', include('selecsosi_django.foo.urls')),

   # Uncomment the admin/doc line below to enable admin documentation:
   # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

   # Uncomment the next line to enable the admin:
   url(r'contact', 'contact', name="contact"),
   url(r'', 'index', name='index'),
)
