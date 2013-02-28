#!/usr/bin/env python

from flask import Flask, render_template, url_for
app = Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html', static_prefix=url_for('static',
    filename=''))

@app.route("/movies/")
@app.route("/movies/<path:path>")
def movies(path=None):
  return "Movie requested, path = '%s'" % path

@app.route("/tv/")
@app.route("/tv/<path:path>")
def tv(path=None):
  return "TV requested, path = '%s'" % path

if __name__ == "__main__":
  app.run(debug=True)
