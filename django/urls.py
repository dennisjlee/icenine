from django.conf.urls.defaults import *
from icenine.ice9.conf import ROOT, DJANGO_ROOT

urlpatterns = patterns('',
    # Example:
    # (r'^icenine/', include('icenine.apps.foo.urls.foo')),
    (r'^$', 'icenine.ice9.views.index'),

    (r'^movies(?P<path>(/.*)?)/$', 'icenine.ice9.views.render', {'type': 'movie'}),
    (r'^movies(?P<path>(/.*)?)/(?P<file>[^/]+)$', 'icenine.ice9.views.download', {'type': 'movie'}),

    (r'^tv(?P<path>(/.*)?)/$', 'icenine.ice9.views.render', {'type': 'tv'}),
    (r'^tv(?P<path>(/.*)?)/(?P<file>[^/]+)$', 'icenine.ice9.views.download', {'type': 'tv'}),

    (r'^software(?P<path>(/.*)?)/$', 'icenine.ice9.views.render', {'type': 'software'}),
    (r'^software(?P<path>(/.*)?)/(?P<file>[^/]+)$', 'icenine.ice9.views.download', {'type': 'software'}),

    (r'recent', 'icenine.ice9.views.recent'),

    # Uncomment this for admin:
#    (r'^admin/', include('django.contrib.admin.urls')),
#) # comment out these two parens to turn on devel static file serving
#( 
    # for DEVELOPMENT ONLY!!
    (r'^include/(?P<path>.*)$', 'django.views.static.serve', 
                                {'document_root':
                                 ROOT + '/static/include/'}),
    (r'^thumbs/movies/(?P<path>.*)$', 'django.views.static.serve', 
                                      {'document_root':
                                       ROOT + '/static/thumbs/movies/'}),
    (r'^thumbs/tv/(?P<path>.*)$', 'django.views.static.serve', 
                                      {'document_root':
                                       ROOT + '/static/thumbs/tv/'}),
    (r'^thumbs/software/(?P<path>.*)$', 'django.views.static.serve', 
                                      {'document_root':
                                       ROOT + '/static/thumbs/software/'}),
)
