from django.conf import settings
from django.conf.urls import patterns, include, url
#!chuck_renders URL_MODULES #!end


#!chuck_renders URLS
urlpatterns = patterns('',
)

# static media
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
#!end
