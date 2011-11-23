#!/usr/bin/env python

import os, re, sys, getopt
from datetime import datetime
from icenine.ice9.conf import DIR_CONF
from icenine.ice9.models import *
from MySQLdb.connections import OperationalError


def usage():
  print """
%s: 

  -h, --help  show this usage message
  -v, --verbosity  verbosity level: from 0-2 (default 0)
  -m, --modified_time  insert new files into db using the file's modification time
                      (default is to use current time)
  -d, --debug  don't actually write to the database, just print messages for debugging
""" % sys.argv[0]

_usemodifiedtime = False
_verbosity = False
_debug = False

def main(argv):
  global _usedmodifiedtime, _verbosity, _debug
  try:
    opts, args = getopt.getopt(argv, "hv:md", ["help", "verbosity", "modified_time", "debug"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  
  for opt, val in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-d", "--debug"):
      _debug = True
    elif opt in ("-v", "--verbosity"):
      _verbosity = int(val)
    elif opt in ("-m", "--modified_time"):
      _usemodifiedtime = True

  if not _debug:
    # TODO(djlee): this is way too destructive!  could be several minutes where
    # site would report nothing found.
    # instead, do bookkeeping in python and set things to 'not found' at the end
    Directory.set_all_not_found()
    File.set_all_not_found()

  for (type, conf) in DIR_CONF.items():
    print "\n\n#########\nUpdating " + type + "\n#########\n"
    # stick in a compiled regex to the struct for use in process_files
    conf.regex = re.compile(r'.*\.(%s)$' % '|'.join(conf.file_extensions), re.I)
    for directory in conf.local_fileroot:
      # make sure there's a trailing slash
      if directory[-1] not in ('/', '\\'):
        directory += '/'
      for curdir, subdirs, files in os.walk(directory, topdown=True):
        process_files(conf, directory, curdir, files)

# TODO(djlee): bookkeeping to avoid set_all_not_found
# root = Directory.objects.get(name='/', type=type)
# root.subdirs.all()
# root.files.all()

def process_files(conf, root, curdir, files):
  foundany = False
  relative_path = curdir.replace(root, '').replace(os.sep, '/')
  (parent, dirname) = os.path.split(relative_path)

  # get_or_create saves the new directory right away if it was created
  (d, newdir) = Directory.objects.get_or_create(type=conf.type, 
      relative_path__iexact=relative_path, 
      defaults = {'found': False, 'name': dirname, 
                  'relative_path': relative_path})
  if _verbosity >= 1:
    print "Processing %s directory, %s" % (newdir and "NEW" or "OLD", curdir)
    print "Relative path: " + relative_path

  for file in files:
    if not conf.regex.match(file):
      continue

    foundany = True
    # TODO fix this copout, find out how the extra slash actually sneaks in ..
    absolute_path = (curdir + '/' + file).replace('//', '/')

    # TODO(djlee): there is something wrong with the encoding that is passed to
    # MySQL.  perhaps a Django or MySQLdb setting.  effect is that INSERTs with 
    # accented characters fail.

    # convert Windows Latin-1 encoding to UTF8, which is what MySQL expects
    #file = unicode(file, 'iso-8859-1').encode('utf-8')

    if relative_path == "":
      relative_file_path = file
    else:
      relative_file_path = (relative_path + '/' + file).replace('//', '/')


    # this does NOT save the File object right away if it was created
    try: 
      f = File.objects.get(type=conf.type, relative_path__iexact=relative_file_path)
      newfile = False
    except File.DoesNotExist:
      f = File(type=conf.type, name=file, relative_path=relative_file_path)
      newfile = True

    if _verbosity >= 2:
      print "Processing %s file, %s" % (newfile and "NEW" or "OLD", file)
      print "Relative path: " + relative_file_path
      if not newfile and f.path != absolute_path:
        print "Old path: %s\nNew path: %s" % (f.path, absolute_path)
      else:
        print "Absolute path: " + absolute_path

    f.found = True
    f.path = absolute_path
    stat = os.stat(absolute_path)
    f.size = stat.st_size
    if newfile:
      if _usemodifiedtime:
        time = datetime.fromtimestamp(stat.st_mtime)
      else:
        time = datetime.now()
      f.addition_date = time
      f.directory = d
    try: 
      f.save()
    except Exception, e:
      print "File save caused exception: " + str(f)
      print e
      print "Skipping..."
    else:
      if conf.type == 'tv' or conf.type == 'movie':
        f.make_thumb()

  if newdir:
    try:
      p = Directory.objects.filter(type=conf.type).get(relative_path__iexact=parent)
    except:
      print "Directory get caused problems: path was %s" % parent
      raise
    d.parent = p
    if _verbosity >= 1:
      print "Setting parent of new directory %s to be %s" % (str(d), str(p))
  if foundany:
    d.found = True
    d.save()

if __name__ == "__main__":
    main(sys.argv[1:])
