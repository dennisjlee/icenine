#!/usr/bin/env python

import os, re, sys, tempfile, random, shutil, subprocess
from os.path import exists
import icenine.ice9.conf

# Returns whether thumbnail was created
def make_movie_thumb(frames_file, thumb_file, video_file, conf):
  if (not exists(frames_file) or not exists(video_file) or exists(thumb_file)):
    return False
  
  frames = open(frames_file)
  framenums = [int(line) for line in frames.readlines()]
  framenum = random.randrange(framenums[0], framenums[1]+1)
  frames.close()

  # Touch file so we get a zero-sized one in case we fail
  thumb = open(thumb_file, 'w')
  thumb.close()

  try:
    midentify_cmd = u'%s "%s"' % (icenine.ice9.conf.MIDENTIFY, video_file)
    midentify_pipe = subprocess.Popen(midentify_cmd,
                                      shell=True,
                                      stdout=subprocess.PIPE).stdout
    midentify_out = midentify_pipe.read()
    midentify_pipe.close()
  except Exception as e:
    print "Error making thumbnail for file: %s" % video_file.encode('ascii', 'xmlcharrefreplace')
    print e
    return False

  success = False

  if (midentify_out.find('ID_VIDEO_CODEC') >= 0):
    m = re.search(r'ID_VIDEO_FPS=(\S*)\s', midentify_out)
    if not m:
      return False
    fps = float(m.group(1))

    m = re.search(r'ID_LENGTH=(\S*)\s', midentify_out)
    if not m:
      return False
    length = float(m.group(1))

    time = min(framenum / fps, length * 0.9)
    
    tempdir = tempfile.mkdtemp()
    prev_cwd = os.getcwd()
    os.chdir(tempdir)

    # output 2 frames, because the first one is sometimes the first frame
    # of file instead of at a point in the middle.  
    mplayer_cmd = u'%s -nosound -vo jpeg:outdir=. -ss %.3f -frames 2 "%s"' % \
        (icenine.ice9.conf.MPLAYER, time, video_file)
    subprocess.call(mplayer_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    output_jpg = "temp.jpg"
    convert_cmd = u'%s -geometry %sx%s 00000002.jpg "%s"' % \
        (icenine.ice9.conf.IMAGEMAGICK_CONVERT, conf.thumb_width,
            conf.thumb_height, output_jpg)

    subprocess.call(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if (exists(output_jpg)):
      success = True
      shutil.move(output_jpg, thumb_file)

    # Clean up
    os.chdir(prev_cwd)
    shutil.rmtree(tempdir)

  return success
