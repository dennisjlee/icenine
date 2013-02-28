from os import path
from configobj import ConfigObj, flatten_errors
from django.template.defaultfilters import urlencode
from validate import Validator

ROOT = 'c:/Inetpub'
DJANGO_ROOT = 'c:/Inetpub/django'

TEMP_DIR = None
MPLAYER = None
MIDENTIFY = None
_MIDENTIFY_TEMPLATE = '%s -vo null -ao null -frames 0 -identify'
IMAGEMAGICK_CONVERT = None

DIR_CONF = {}

def init_config():
  "Initialize config from config.ini file and configspec.ini template file."
  dir = path.dirname(__file__)
  config = ConfigObj(path.join(dir, 'config.ini'),
                     configspec=path.join(dir, 'configspec.ini'))
  validator = Validator()
  results = config.validate(validator)

  if results != True:
    for (section_list, key, _) in flatten_errors(config, results):
      if key is not None:
        print 'The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list))
      else:
        print 'The following section was missing: %s ' % ', '.join(section_list)
  
  TEMP_DIR = config['temp_dir']
  MPLAYER = config['mplayer']
  MIDENTIFY = _MIDENTIFY_TEMPLATE % MPLAYER
  IMAGEMAGICK_CONVERT = config['imagemagick_convert']

  DIR_CONF['tv'] = TVConf(config['directories'])
  DIR_CONF['movie'] = MovieConf(config['directories'])


class DirConf:
  def __init__(self, 
               config,
               type = '',
               webroot = '',
               section = ''):

    self.type = type 
    self.webroot = webroot
    self.section = section

    self.index_rows = config['index_rows']
    self.index_cols = config['index_cols']
    self.thumb_width = config['thumb_width']
    self.thumb_height = config['thumb_height']
    self.style = config['style']
    self.buttons = config['buttons']
    self.default_thumb = config['default_thumb']

    subconfig = config[section]
    self.local_fileroot = subconfig['local_fileroot']
    self.local_thumbroot = subconfig['local_thumbroot']
    self.file_extensions = subconfig['file_extensions']

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
  def __init__(self, config):
    DirConf.__init__(self,
        type='tv',
        webroot='/tv',
        section='tv',
        config=config)
    
  def get_default_subdir_infolink(self, d):
    return "http://www.google.com/search?q=site:epguides.com&q=%s&btnI=I'm+Feeling+Lucky" \
        % urlencode(d.label())


##########
# Movies #
##########
class MovieConf(DirConf):
  def __init__(self, config):
    DirConf.__init__(self,
        type='movie',
        webroot='/movies',
        section='movies',
        config=config)

  def get_default_file_infolink(self, f):
    label = self.label()
    label = re.sub(r' CD ?\d$', '', label) # 2-part movies, CD1 or CD2
    label = re.sub(r' \(.*\)$/', '', label) # get rid of parenthesized notes
    return "http://www.imdb.com/find?q=" + urlencode(label)
