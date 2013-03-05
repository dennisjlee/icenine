#!/usr/bin/env python

import re, sys, getopt

from icenine.ice9 import conf
from icenine.ice9.models import *
from MySQLdb.connections import OperationalError
from pymongo import MongoClient, ASCENDING, DESCENDING

def main(args):
  conf.init_config()
  conn = MongoClient()
  db = conn.icenine

  db.directories.drop()
  for dir in Directory.objects.filter(found=True):
    try:
      if dir.parent_id is None or dir.parent:
        d = {'_id': dir.id,
             'type': dir.type,
             'name': dir.name,
             'parent_id': dir.parent_id,
             'found': dir.found,
             'relative_path': dir.relative_path}
        if dir.info_link:
          d['info_link'] = dir.info_link
        db.directories.insert(d)
    except Directory.DoesNotExist:
      print 'Directory %s, parent id %d does not exist!' % (dir.relative_path,
          dir.parent_id)
  db.directories.ensure_index([('type', ASCENDING), ('relative_path', ASCENDING)],
      unique=True, dropDups=True)
  db.directories.ensure_index([('parent_id', ASCENDING), ('name', ASCENDING)],
      unique=True, dropDups=True)

  db.files.drop()
  for file in File.objects.filter(found=True):
    if db.directories.find_one({'_id': file.directory_id}):
      f = {'_id': file.id,
           'type': file.type,
           'name': file.name,
           'path': file.path,
           'size': file.size,
           'addition_date': file.addition_date,
           'parent_id': file.directory_id,
           'found': file.found,
           'relative_path': file.relative_path}
      if file.info_link:
        f['info_link'] = file.info_link
      try:
        if file.movie:
          # Note that Mongo can't store Decimals.. https://jira.mongodb.org/browse/SERVER-1393
          f['movie_info'] = {
              'keywords': re.split(r'\s*,\s*', file.movie.keywords),
              'rating': int(file.movie.rating * 1000)}
      except Movie.DoesNotExist:
        pass
      db.files.insert(f)
    else:
      print 'File %s, parent directory %d does not exist in Mongo!' % (file.relative_path,
          file.directory_id)
  db.files.ensure_index([('parent_id', ASCENDING), ('name', ASCENDING)],
      unique=True, dropDups=True)
  db.files.ensure_index([('addition_date', DESCENDING)])


if __name__ == '__main__':
    main(sys.argv)
