#!/usr/bin/env python

from flask import Flask, abort, render_template, request, url_for
from flask.ext.pymongo import PyMongo
from bson import json_util
import json

app = Flask(__name__)
app.config.from_object('icenine2.settings')
app.config.from_envvar('ICENINE_SETTINGS')
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

mongo = PyMongo(app)

@app.route('/', defaults={'path': None})
def index(path):
  # TODO: render json for initial bootstrap
  return render_template('index.jade',
      static_prefix=url_for('static', filename=''),
      use_cdn=app.config['USE_CDN'])

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

# TODO: id parsing below may need to change when using Mongo-generated object
# ids instead of mysql-generated numeric ids

@app.route('/api/subdirs/<int:parent_id>')
def subdirs_api(parent_id):
  return mongo_jsonify(fetch_entities(mongo.db.directories, parent_id))

@app.route('/api/files/<int:parent_id>')
def files_api(parent_id):
  return mongo_jsonify(fetch_entities(mongo.db.files, parent_id))

def fetch_entities(table, parent_id):
  entities = list(table.find({'parent_id': parent_id, 'found': True},
      EXCLUDE_FIELDS))
  for e in entities:
    e['thumb_path'] = url_for('static',
        filename=('thumbs/' + e['type'] + '/' + e['relative_path'] + '.jpg'))
    print e['thumb_path']
    del e['relative_path']
    del e['type']
  return entities

if __name__ == '__main__':
  app.run(debug=True)
