#django.wsgi
import os
import sys
import site
import django.core.handlers.wsgi

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
site.addsitedir('$VIRTUALENV_BASEDIR/$SITE_NAME/lib/python2.7/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.dev'
application = django.core.handlers.wsgi.WSGIHandler()
