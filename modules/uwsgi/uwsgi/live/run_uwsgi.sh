#!/bin/bash
rm -f /var/run/uwsgi/$SITE_NAME.sock
uwsgi -p 1 -C -A 4 -m -s /var/run/uwsgi/$SITE_NAME.sock \
 --wsgi-file $PROJECT_BASEDIR/$SITE_NAME/django.wsgi \
 --pythonpath $PROJECT_BASEDIR/$SITE_NAME/$PROJECT_NAME \
 --pythonpath $VIRTUALENV_BASEDIR/$SITE_NAME/lib/python2.7/site-packages \
 --pidfile /var/run/uwsgi/$SITE_NAME.sock
