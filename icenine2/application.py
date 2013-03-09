#!/usr/bin/env python

from flask import Flask, render_template, request, url_for
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


@app.route("/api/movies/")
@app.route("/api/movies/<path:path>")
def movies(path=None):
  if path is not None and path[-1] != '/':
    f = mongo.db.files.find_one({'type': 'movie', 'relative_path': path})
    return mongo_jsonify(f)
  else:
    if path is None:
      path = ''
    else:
      path = path[:-1]
    d = mongo.db.directories.find_one({'type': 'movie', 'relative_path':
        path, 'found': True})
    # TODO: load and serialize child directories and child files
    return mongo_jsonify(d)
  return "Movie requested, path = '%s'" % path

@app.route("/api/tv/")
@app.route("/api/tv/<path:path>")
def tv(path=None):
  return "TV requested, path = '%s'" % path

if __name__ == "__main__":
  app.run(debug=True)
