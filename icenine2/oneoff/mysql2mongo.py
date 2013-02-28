#!/usr/bin/env python

import sys, getopt

from icenine.ice9 import conf
from icenine.ice9.models import *
from MySQLdb.connections import OperationalError

def main(args):
  conf.init_config()
  dirs = Directory.objects.all()
  print dirs

if __name__ == "__main__":
    main(sys.argv)
