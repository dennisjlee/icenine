from django import template

register = template.Library()

### Custom Filters

@register.filter
def sort(val):
  return sorted(val)

@register.filter
def unzip(zipped_list):
  return ([a for (a, _) in zipped_list], [b for (_, b) in zipped_list])

@register.filter
def remove_underscores(str):
  return str.replace('_', ' ')

@register.filter
def chunk_list(list, n):
  """Chunk a list into a list of sublists of length n. 
  Last sublist may be smaller than n depending on the length of input list.
  """
  try:
    n = int(n)
  except ValueError:
    return list
  return [list[x:x+n] for x in range(0, len(list), n)]


### Custom Tags
