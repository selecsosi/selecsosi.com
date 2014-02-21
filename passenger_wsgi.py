import sys, os
INTERP = "/home/selecsosi/opt/python-2.7.3/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

# sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'selecsosi_django'))

os.environ['DJANGO_SETTINGS_MODULE'] = "selecsosi_django.settings"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

