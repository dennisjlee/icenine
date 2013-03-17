var curDir = null;

var PATH_TO_TYPES = {
  'movies': 'movie',
  'tv': 'tv'
};

var File = Backbone.Model.extend({
  idAttribute: "_id",
  url: function() {
    return '/api/metadata/' + this.fullPath();
  },
  fullPath: function() {
    return this.get('type') + '/' + this.get('relative_path');
  },
  additionDate: function() {
    if (this.has('addition_date')) {
      return new Date(this.get('addition_date')['$date']);
    }
    return null;
  }
});

var Directory = Backbone.Model.extend({
  idAttribute: "_id",
  url: function() {
    return '/api/metadata/' + this.fullPath();
  },
  fullPath: function() {
    return this.get('type') + '/' + this.get('relative_path') +
        ((this.get('relative_path') != '') ? '/' : '');
  },
  initialize: function() {
    this.subdirs = new Directories([], {parent: this});

    this.files = new Files([], {parent: this});
  }
});

var Directories = Backbone.Collection.extend({
  model: Directory,
  url: function() {
    return '/api/subdirs/' + this.parent.id;
  },
  initialize: function(models, options) {
    this.parent = options.parent;
  }
});


var Files = Backbone.Collection.extend({
  model: File,
  url: function() {
    return '/api/files/' + this.parent.id;
  },
  initialize: function(models, options) {
    this.parent = options.parent;
  }
});

var IndexView = Backbone.View.extend({
  // TODO: use a template and spruce this up
  render: function() {
    this.$el.html(
        '<a data-fragment="movies/" href="movies/">Movies</a>' +
        '<br>' +
        '<a data-fragment="tv/" href="tv/">TV</a>');
    return this;
  },

  events: {
    'click a': function(e) {
      e.preventDefault();
      Backbone.history.navigate(e.target.getAttribute('data-fragment'),
          {'trigger': true});
    }
  }
});

var DirectoryView = Backbone.View.extend({
  initialize: function() {
    this.listenTo(this.model, "change", this.render);
  },

  render: function() {
    this.$el.html('This is directory ' + this.model.fullPath());
  }
});

var IcenineRouter = Backbone.Router.extend({
  routes: {
    '':             'index',
    'tv/*path':     'tv',
    'movies/*path': 'movies'
  },

  index: function() {
    var indexView = new IndexView();
    indexView.render();
    $('#content').append(indexView.el);
  },

  tv: function(path) {
    if (path == '') path = '/';
    if (path[path.length - 1] == '/') {
      if (!(curDir &&
          curDir.get('type') == 'tv' &&
          curDir.get('relative_path') == path)) {
        curDir = new Directory({
          'type': 'tv',
          'relative_path': path.substr(0, path.length - 1)
        });
        curDir.fetch();
        var view = new DirectoryView({
          model: curDir
        });
        $('#content').empty().append(view.el);
      } else {
        var view = new DirectoryView({
          model: curDir
        });
        view.render();
        $('#content').empty().append(view.el);
      }
    }
  },

  movies: function(path) {
    console.log('navigated to movies with path ' + path);
  }

});

var router = new IcenineRouter();
Backbone.history.start({pushState: true});
