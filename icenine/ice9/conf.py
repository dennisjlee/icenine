from django.template.defaultfilters import urlencode

ROOT = 'c:/Inetpub'
DJANGO_ROOT = 'c:/Inetpub/django'

TEMP_DIR = 'c:/cygwin/tmp'
MPLAYER = 'c:/Progra~1/SMPlayer/mplayer/mplayer.exe'
MIDENTIFY = '%s -vo null -ao null -frames 0 -identify' % MPLAYER
IMAGEMAGICK_CONVERT = 'c:/Progra~1/ImageMagick-6.6.3-Q16/convert.exe'

DIR_CONF = {}

class DirConf:
  def __init__(self, 
               type = '',
               local_fileroot = [],
               local_thumbroot = '',
               webroot = '',
               section = '',
               file_extensions = [],
               index_rows = 100,
               index_cols = 5,
               thumb_width = 130,
               thumb_height = 98,
               style = 'Black.css',
               buttons = 'dark-matte',
               default_thumb = 'movie.gif'):

    self.type = type 
    self.local_fileroot = local_fileroot
    self.local_thumbroot = local_thumbroot
    self.webroot = webroot
    self.section = section
    self.file_extensions = file_extensions
    self.index_rows = index_rows
    self.index_cols = index_cols
    self.thumb_width = thumb_width
    self.thumb_height = thumb_height
    self.style = style
    self.buttons = buttons
    self.default_thumb = default_thumb

  def get_default_thumb(self):
    return '/include/res/actions/%s/%s' % (self.buttons, self.default_thumb)

  def get_default_subdir_infolink(self, d):
    return ''

  def get_default_file_infolink(self, f):
    return ''

######
# TV #
######
class TVConf(DirConf):
  def __init__(self):
    DirConf.__init__(self,
      type = 'tv',
      local_fileroot = ['%s:/tv' % x for x in ['c','d','e','g','h','i','j','k']],
      local_thumbroot = ROOT + '/static/thumbs/tv',
      webroot = '/tv',
      section = 'tv',
      file_extensions = ["avi", "mpg", "ogm", "mov", "wmv",
          "asf", "rm", "rmvb", "mkv", "mp4", "m4v"],
    )
    
  def get_default_subdir_infolink(self, d):
    return "http://www.google.com/search?q=site:epguides.com&q=%s&btnI=I'm+Feeling+Lucky" \
        % urlencode(d.label())

DIR_CONF['tv'] = TVConf()
  

##########
# Movies #
##########
class MovieConf(DirConf):
  def __init__(self):
    DirConf.__init__(self,
      type = 'movie',
      local_fileroot = ['d:/Movies', 'e:/Movies', 'g:/movies', 'h:/movies', ],
      local_thumbroot = ROOT + '/static/thumbs/movies',
      webroot = '/movies',
      section = 'movies',
      file_extensions = ["avi", "mpg", "ogm", "mov", "wmv", "mp4", "m4v"],
    )

  def get_default_file_infolink(self, f):
    label = self.label()
    label = re.sub(r' CD ?\d$', '', label) # 2-part movies, CD1 or CD2
    label = re.sub(r' \(.*\)$/', '', label) # get rid of parenthesized notes
    return "http://www.imdb.com/find?q=" + urlencode(label)

DIR_CONF['movie'] = MovieConf()


############
# Software #
############
class SoftwareConf(DirConf):
  def __init__(self):
    DirConf.__init__(self,
      type = 'software',
      local_fileroot = ['h:/Software'],
      local_thumbroot = ROOT + '/static/thumbs/software',
      webroot = '/software',
      section = 'software',
      file_extensions = ["zip", "rar", "txt", "iso"],
      index_rows = 100,
      index_cols = 4,
      thumb_width = 150,
      thumb_height = 150,
      style = 'White.css',
      buttons = 'bright-matte',
      default_thumb = 'software.gif',
    )

  def get_default_subdir_infolink(d): 
    return "http://www.google.com/search?q=" + urlencode(d.label())

  def get_default_file_infolink(f): 
    return "http://www.google.com/search?q=" + urlencode(f.label())

DIR_CONF['software'] = SoftwareConf()
