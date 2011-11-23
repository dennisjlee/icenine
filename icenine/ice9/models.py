from django.conf import settings
from django.db import models
import django.contrib.auth.models
import icenine.ice9.conf
import icenine.ice9.thumbnails
import math, os, re

CATEGORY_CHOICES = (
    ('movie', 'Movie'),
    ('tv', 'TV'),
    ('software', 'Software')
)

# BigIntegerField class taken from http://code.djangoproject.com/ticket/399
class BigIntegerField(models.IntegerField):
  empty_strings_allowed=False
  def get_internal_type(self):
    return "BigIntegerField"
  
  def db_type(self):
    if settings.DATABASE_ENGINE == 'oracle':
      return 'NUMBER(19)'
    else:
      return 'bigint'


# hmm ported this function from PHP but it's not needed ...
# django has a built-in filter for this!
def human_readable_size(bytes):
  if bytes == 0:
    return "0 Bytes"
  # this is for 1 GB = 2^30 bytes, 1 TB = 2^40 bytes
  # This is what Windows uses... 
  # but this is technically gibibytes and tebibytes... sigh
  formats = ["%d Bytes", "%.1f KB", "%.1f MB", "%.2f GB", "%.3f TB"]
  logsize = min(int(math.log(bytes)/math.log(1024)), len(formats)-1)
  return formats[logsize] % (bytes / math.pow(1024, logsize))

class Directory(models.Model):
  type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, 
    db_index=True)
  name = models.CharField(max_length=150, db_index=True)
  parent = models.ForeignKey('self', null=True, blank=True, db_index=True,
    related_name='subdirs')
  found = models.BooleanField(db_index=True)
  info_link = models.CharField(max_length=255, blank=True, default='')
  relative_path = models.CharField(max_length=255, db_index=True)
  
  class Meta:
    unique_together = (("type", "name", "parent"),)
    verbose_name = 'Directory'
    verbose_name_plural = 'Directories'

  def __str__(self):
    return self.absolute_path()
    #return self.type + ":/" + self.name + "/"

  class Admin: pass

  def friendly_label(self):
    label = self.label()
    if label == '/':
      label = self.conf().section + '/'
    return label

  def label(self):
    label = self.name.replace('_', ' ')
    if label[-1] != '/':
      label += '/'
    return label

  def conf(self):
    return icenine.ice9.conf.DIR_CONF[self.type]

  def get_relative_path(self):
    if self.parent == None:
      return ''
    else: 
      parent_relative_path = self.parent.get_relative_path()
      if parent_relative_path:
        parent_relative_path += '/'
      return parent_relative_path + self.name

  def get_info_link(self):
    return self.info_link or self.conf().get_default_subdir_infolink(self)

  def absolute_path(self):
    relative_path = self.relative_path
    if relative_path:
      relative_path = '/' + relative_path
    return self.conf().webroot + relative_path

  def thumb_image(self):
    hasthumb = False
    thumbroot = self.conf().local_thumbroot
    d = self
    while not hasthumb and d != None:
      thumb_path = '/thumbs%s.jpg' % d.absolute_path()
      local_thumb = '%s/%s.jpg' % (thumbroot, d.relative_path)
      if os.path.isfile(local_thumb) and os.path.getsize(local_thumb) > 0:
        hasthumb = True
        break
      d = d.up()
    thumb_image = hasthumb and thumb_path or self.conf().get_default_thumb()
    return thumb_image

  def up(self):
    return self.parent

  @staticmethod
  def set_all_not_found():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("UPDATE ice9_directory SET found=0")


class File(models.Model):
  type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, 
    db_index=True)
  name = models.CharField(max_length=150, db_index=True)
  path = models.CharField(max_length=255, unique=True)
  size = BigIntegerField()
  addition_date = models.DateTimeField(auto_now_add=True, db_index=True)
  found = models.BooleanField(db_index=True)
  directory = models.ForeignKey(Directory, db_index=True, related_name='files')
  info_link = models.CharField(max_length=255, blank=True, default='')
  relative_path = models.CharField(max_length=255, db_index=True)

  def __str__(self): return self.name

  class Admin: pass

  def conf(self):
    return icenine.ice9.conf.DIR_CONF[self.type]
  
  def label(self):
    ind = self.name.rfind('.')
    if ind < 0:
      return self.name
    else:
      return self.name[0:ind]

  def get_relative_path(self):
    relative_path = self.directory.relative_path
    if relative_path:
      relative_path += '/'
    return relative_path + self.name

  def absolute_path(self):
    return self.directory.absolute_path() + '/' + self.name

  def get_info_link(self):
    return self.info_link or self.conf().get_default_file_infolink(self)

  def readable_size(self):
    return human_readable_size(self.size)

  # TODO(djlee): below is outdated.. remove?

  # returns the path to this file's thumbnail, were it to exist.
  # Used for thumbnail generation; if looking for the actual image to use as 
  # a thumbnail for this file, use file.thumb_image().
  #def thumb_path(self):
  #  return '/thumbs%s.jpg' % self.absolute_path()

  def thumb_image(self):
    hasthumb = False
    thumbroot = self.conf().local_thumbroot
    d = self
    while not hasthumb and d != None:
      thumb_path = '/thumbs%s.jpg' % d.absolute_path()
      local_thumb = '%s/%s.jpg' % (thumbroot, d.relative_path)
      if os.path.isfile(local_thumb) and os.path.getsize(local_thumb) > 0:
        hasthumb = True
        break
      d = d.up()
    thumb_image = hasthumb and thumb_path or self.conf().get_default_thumb()
    return thumb_image

  def make_thumb(self):
    assert self.type != 'software', "make_thumb not supported for software files!"
    frames_prefix = self.directory.relative_path
    if (frames_prefix):
      frames_prefix = frames_prefix + '.'
    thumbroot = self.conf().local_thumbroot 
    frames_file = "%s/%sframes" % (thumbroot, frames_prefix)
    thumb_file = "%s/%s.jpg" % (thumbroot, self.relative_path)
    icenine.ice9.thumbnails.make_movie_thumb(frames_file, thumb_file, self.path, 
        self.conf())

  def up(self):
    return self.directory

  @staticmethod
  def set_all_not_found():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("UPDATE ice9_file SET found=0")


class Movie(models.Model):
  file = models.OneToOneField(File, primary_key=True)
  keywords = models.CharField(max_length=255, blank=True)
  rating = models.DecimalField(max_digits=6, decimal_places=3, db_index=True)

  def __str__(self): return str(self.file)

  class Admin: pass

  def readable_keywords(self):
    return self.keywords.replace(',', ', ')


class User(models.Model):
  user = models.OneToOneField(django.contrib.auth.models.User, 
                              null=True,
                              primary_key=True)
  legacy_id = models.IntegerField(unique=True)
  email = models.EmailField(db_index=True)
  full_name = models.CharField(max_length=255, blank=True)
  comment = models.CharField(max_length=255, blank=True)
  addition_date = models.DateTimeField()

  def __str__(self): return self.email

  class Admin: pass


class Log(models.Model):
  completed = models.BooleanField()
  user = models.ForeignKey(User, to_field='legacy_id', db_index=True)
  file = models.ForeignKey(File, db_index=True)
  start_time = models.DateTimeField(auto_now_add=True, db_index=True)
  end_time = models.DateTimeField(null=True)
  error_message = models.CharField(max_length=255, blank=True)
  ip_address = models.IPAddressField(db_index=True)

  def __str__(self):
    return "'%s' by '%s' at %s" % (self.file, self.user, self.start_time)

  class Admin: pass
