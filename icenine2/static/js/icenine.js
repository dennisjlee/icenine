var IcenineRouter = Backbone.Router.extend({
  routes: {
    '':             'index',
    'tv/*path':     'tv',
    'movies/*path': 'movies'
  },

  index: function() {
    console.log('navigated to index');
  },

  tv: function(path) {
    console.log('navigated to tv with path ' + path);
  },

  movies: function(path) {
    console.log('navigated to movies with path ' + path);
  }

});

var router = new IcenineRouter();
Backbone.history.start({pushState: true});
