#!/usr/bin/env python

import json

from bson import json_util
from flask import (Flask, abort, render_template, request, send_file,
                   send_from_directory, url_for)
from flask.ext.pymongo import PyMongo
from flask.ext.scss import Scss
from pymongo import ASCENDING, DESCENDING

app = Flask(__name__, static_folder='app')
app.config.from_object('icenine2.settings')
app.config.from_envvar('ICENINE_SETTINGS')
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

mongo = PyMongo(app)
Scss(app, static_dir=app.static_folder + '/css', asset_dir=app.static_folder)

@app.route('/', defaults={'path': None})
def index(path):
  # TODO: render json for initial bootstrap
  return send_file('app/index.html')

@app.route('/components/<path:path>')
@app.route('/scripts/<path:path>')
@app.route('/css/<path:path>')
@app.route('/images/<path:path>')
@app.route('/views/<path:path>')
def static_from_root(path):
    return send_from_directory(app.static_folder, request.path[1:])

# Note: tv and movies need separate routes to avoid redirecting from /tv/ to
# /movies/
@app.route('/tv/', defaults={'path': '/'})
@app.route('/tv/<path:path>')
def tv(path):
  return index(path)

@app.route('/movies/', defaults={'path': '/'})
@app.route('/movies/<path:path>')
def movies(path):
  return index(path)

def mongo_jsonify(doc):
  return app.response_class(
      json.dumps(doc, default=json_util.default, indent=None if request.is_xhr else 2),
      mimetype='application/json')

@app.route('/api/metadata/<filetype>/', defaults={'path': '/'})
@app.route('/api/metadata/<filetype>/<path:path>')
def metadata_api(filetype, path):
  if filetype != 'movie' and filetype != 'tv':
    abort(404)

  if path[-1] != '/':
    f = mongo.db.files.find_one({'type': filetype, 'relative_path': path})
    return mongo_jsonify(f)
  else:
    path = path[:-1]
    d = mongo.db.directories.find_one({'type': filetype, 'relative_path':
        path, 'found': True})
    return mongo_jsonify(d)

EXCLUDE_FIELDS = {'parent_id': False, 'found': False}

class EntityTypes:
  FILE = 'file'
  DIRECTORY = 'directory'

@app.route('/api/children/<parent_id>')
def children_api(parent_id):
  children = fetch_entities(EntityTypes.DIRECTORY, parent_id)
  children.extend(fetch_entities(EntityTypes.FILE, parent_id))
  return mongo_jsonify(children)

def fetch_entities(entity_type, parent_id, sort=('name', ASCENDING)):
  try:
    # parent_id could be int (legacy from sql) or mongo id
    int_parent_id = int(parent_id)
    parent_id = int_parent_id
  except ValueError:
    pass
  table = mongo.db.files if entity_type is EntityTypes.FILE else mongo.db.directories
  # TODO: perhaps use `skip` keyword to deal w/ paging
  entities = list(
      table.find({'parent_id': parent_id, 'found': True}, EXCLUDE_FIELDS)
          .sort(*sort))
  for e in entities:
    # TODO: validate thumb path or make it live in the db
    e['thumb_path'] = url_for('static',
        filename=('thumbs/' + e['type'] + '/' + e['relative_path'] + '.jpg'))
    del e['relative_path']
    del e['type']
    if entity_type is EntityTypes.DIRECTORY:
      e['directory'] = True
  return entities

if __name__ == '__main__':
  app.run(debug=True)
