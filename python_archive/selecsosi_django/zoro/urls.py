from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('zoro.views',
     url(r'^$', 'index'),
     url(r'^fib/$', 'fib'),
     url(r'^fib_result/$', 'fib_result'),
)
