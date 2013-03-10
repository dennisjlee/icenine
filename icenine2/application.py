#!/usr/bin/env python

from flask import Flask, abort, render_template, request, url_for
from flask.ext.pymongo import PyMongo
from bson import json_util
import json

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'icenine'
mongo = PyMongo(app)

@app.route("/")
def index():
  return render_template('index.html', static_prefix=url_for('static',
    filename=''))

def mongo_jsonify(doc):
  return app.response_class(
      json.dumps(doc, default=json_util.default, indent=None if request.is_xhr else 2),
      mimetype='application/json')


@app.route("/api/<filetype>/", defaults={'path': '/'})
@app.route("/api/<filetype>/<path:path>")
def movies(filetype, path):
  if filetype != 'movie' and filetype != 'tv':
    abort(404)

  if path[-1] != '/':
    f = mongo.db.files.find_one({'type': filetype, 'relative_path': path})
    return mongo_jsonify(f)
  else:
    path = path[:-1]
    d = mongo.db.directories.find_one({'type': filetype, 'relative_path':
        path, 'found': True})
    exclude_fields = {'_id': False, 'type': False, 'parent_id': False, 'found': False}
    d['subdirectories'] = list(mongo.db.directories.find(
        {'type': filetype, 'parent_id': d['_id'], 'found': True},
        exclude_fields))
    d['files'] = list(mongo.db.files.find(
        {'type': filetype, 'parent_id': d['_id'], 'found': True},
        exclude_fields))
    return mongo_jsonify(d)

if __name__ == "__main__":
  app.run(debug=True)
