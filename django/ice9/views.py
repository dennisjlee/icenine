import os
import sys
from django.shortcuts import render_to_response
from django.http import HttpResponse
from icenine.ice9.models import *


def index(request):
  return render_to_response('index.djhtml')

type2path = { 'movie': 'movies',
              'tv': 'tv',
              'software': 'software' }
type2prefix = { 'movie': 'movies',
                'tv': 'files',
                'software': 'files' }


def render(request, path, type):
  directory = Directory.objects.filter(type=type).get(name='/')
  paths_zipped = []
  cur_path = '/%s/' % type2path[type]
  paths_zipped.append((type2path[type], cur_path))
  if len(path) > 1:
    for path_component in path[1:].split('/'):
      directory = directory.subdirs.get(name=path_component)
      cur_path += path_component + '/'
      paths_zipped.append((path_component, cur_path))

  template = '%s_render_%s.djhtml' % (
      type2prefix[type], (request.REQUEST.has_key('hi') and 'hi' or 'low')
  )

  return render_to_response(template, 
    {'directory': directory,
     'paths_zipped': paths_zipped,
     'subdirs': directory.subdirs.filter(found=True).order_by('name'),
     'files': directory.files.filter(found=True).order_by('name')})


def recent(request):
  files = File.objects.order_by('-addition_date')[:100]
  return render_to_response('recent_files.djhtml', {'files': files})


def download(request, path, file, type):
  # TODO(djlee): real download page for external users ..
  # This is just the internal one that launches the file ..
  if path == "":
    relative_path = file
  else:
    if path[0] == '/':
      path = path[1:]
    relative_path = path + '/' + file
  file = File.objects.filter(type=type).get(relative_path__iexact=relative_path)
  try:
    #os.system('"c:\Program Files\Zoom Player\zplayer.exe" "%s"' % file.path)
    p = os.path.normpath(file.path)
    sys.stderr.write("Launching file, %s\n" % p)
    sys.stderr.flush()
    os.startfile(p)
  except Exception, e:
    sys.stderr.write("Exception when launching local file, %s\n" % e)
    sys.stderr.flush()
    # NOTE(djlee): if file associations get messed up, uncomment the following
    # line to get a zplayer instance launched as the admin user - can fix the
    # associations in there.
    os.system('"c:\Program Files\Zoom Player\zplayer.exe"')
    
    
  html = """
<html>
  <body onload="window.close()"></body>
</html>
"""
  return HttpResponse(html)
