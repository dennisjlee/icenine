#!/usr/bin/env python

from flask import Flask, abort, render_template, request, url_for
from flask.ext.pymongo import PyMongo
from bson import json_util
import json

app = Flask(__name__)
app.config.from_object('icenine2.settings')
app.config.from_envvar('ICENINE_SETTINGS')

mongo = PyMongo(app)

@app.route('/', defaults={'path': None})
def index(path):
  return render_template('index.html',
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

EXCLUDE_FIELDS = {'type': False, 'parent_id': False, 'found': False}

# TODO: id parsing below may need to change when using Mongo-generated object
# ids instead of mysql-generated numeric ids

@app.route('/api/subdirs/<int:parent_id>')
def subdirs_api(parent_id):
  return mongo_jsonify(list(mongo.db.directories.find(
      {'parent_id': parent_id, 'found': True},
      EXCLUDE_FIELDS)))

@app.route('/api/files/<int:parent_id>')
def files_api(parent_id):
  return mongo_jsonify(list(mongo.db.files.find(
      {'parent_id': parent_id, 'found': True},
      EXCLUDE_FIELDS)))

if __name__ == '__main__':
  app.run(debug=True)
