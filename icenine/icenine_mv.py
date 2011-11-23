#!/usr/bin/env python

import os, re, sys, getopt, shutil
from datetime import datetime
from icenine.ice9.conf import DIR_CONF
from icenine.ice9.models import *
from MySQLdb.connections import OperationalError


def usage():
  print """
%s [OPTIONS] source_file dest_file

Moves a file from source_file to dest_file, and updates the icenine database
with the new file path.  DOES NOT YET SUPPORT MOVING DIRECTORIES OR MOVING
FILES TO A DIFFERENT DIRECTORY.

  -h, --help  show this usage message
  -v, --verbose  print verbose messages
  -d, --debug  don't actually write to the database, just print messages for debugging
""" % sys.argv[0]


_verbose = False
_debug = False


def main(argv):
  global _verbose, _debug

  try:
    opts, args = getopt.getopt(argv, "hvd", ["help", "verbose", "debug"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  for opt, val in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-d", "--debug"):
      _debug = True
    elif opt in ("-v", "--verbose"):
      _verbose = True

  if len(args) != 2:
    print "Args was %d long (%s)" % (len(args), "|".join(args))
    usage()
    sys.exit(2)

  source = args[0].replace('\\', '/')
  dest = args[1].replace('\\', '/')

  try: 
    f = File.objects.get(name__iexact=source)
    newfile = False
  except File.DoesNotExist:
    print "Source file %s does not exist in database!" % source
    sys.exit(2)

  if not _debug:
    try:
      # TODO(djlee): possible case-sensitivity probs below ..
      # NOTE(djlee): this all assumes that the paths passed into this
      # script have no directory components.  Garrrr... 
      f.name = dest
      f.relative_path = f.relative_path.replace(source, dest)
      f.path = f.path.replace(source, dest)
      f.save()
      shutil.move(source, dest)
    except:
      print "Error moving %s to %s!" % (source, dest)
      raise

  if _verbose or _debug:
    print "%s -> %s" % (source, dest)

if __name__ == "__main__":
    main(sys.argv[1:])
