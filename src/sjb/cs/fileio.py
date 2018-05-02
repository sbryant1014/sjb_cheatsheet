"""Module responsible for reading/writing cheat sheet json to file."""
import os
import json
import warnings
import sjb.cs.classes
import sjb.cs.display


DEFAULT_LIST_FILE='cheatsheet'

def _get_user_data_dir():
  """Gets the default dir where applications can store data for this user."""
  if 'XDG_DATA_HOME' in os.environ:
    return os.environ['XDG_DATA_HOME']
  return os.path.join(os.environ['HOME'], '.local', 'share')

def _get_app_data_dir():
  """Gets the default dir for this application's data for this user."""
  return os.path.join(_get_user_data_dir(), 'sjb', 'cheatsheet')

def _get_default_list_file(list=None):
  """Gets the full pathname of the cheatsheet file named list.

  Note: list should not have an extension.
  """
  list = list or DEFAULT_LIST_FILE
  return os.path.join(_get_app_data_dir(), list + '.json')

def _encode_entry(entry):
  entry.validate()
  return {
    'oid': entry.oid,
    'primary': entry.primary,
    'tags': list(entry.tags),
    'clue': entry.clue,
    'answer': entry.answer
  }

def _decode_entry(json_object):
  return(sjb.cs.classes.Entry(
    clue=json_object['clue'],
    answer=json_object['answer'],
    primary=json_object['primary'],
    tags=set(json_object['tags']),
    oid=json_object['oid']))

def save_cheatsheet(cs, list=None, listpath=None):
  """Saves a cheatsheet list to a json file.

  Arguments:
    list: str An optional local list name to save the cheatsheet list as. The 
      resulting file is saved in the default application directory with the
      local file name 'list.json'. This argument is mututally exclusive with 
      listpath.
    listpath: str An optional full path name to save the cheatsheet list to.
      This argument is mututally exclusive with listpath.

  Raises:
    Exception: If both list and listpath are given.
  """
  if list and listpath:
    raise Exception(
      'Cannot set both list and listpath args (this should never happen')

  # First check list/listpath arguments, then try the file that the cheatsheet 
  # was read from. If none of those exist, use the default list file.
  # TODO: reconsider this logic. Is this really the best behavior?
  if list:
    fname = _get_default_list_file(list=list)
  else:
    fname = listpath or cs.source_filename or _get_default_list_file()


  top_json = {
    'cheatsheet': {
      'version': cs.version,
      'modified_date': cs.modified_date,
      'entries': [_encode_entry(e) for e in cs.items]
    }
  }

  fname = fname or cs.source_filename or _get_default_list_file()
  json_file = open(fname, "w")

  json_file.write(json.dumps(top_json, indent=2))

def load_cheatsheet(list=None, listpath=None):
  """Loads a cheat sheet from a json file.

  Arguments:
    list: str An optional local list name to read the cheatsheet from. This 
      looks for a file in the default application directory with the local 
      file name 'list.json'. This argument is mututally exclusive with 
      listpath.
    listpath: str An optional full path name to read the cheatsheet from. 
      This argument is mututally exclusive with listpath.

  Returns:
    CheatSheet: object with contents given by the loaded file.

  Raises:
    Exception: If both list and listpath are given.
  """
  if list is not None and listpath is not None:
    raise Exception(
      'Cannot set both list and listpath args (this should never happen.)')

  fname = listpath or _get_default_list_file(list=list)

  # If file doesn't exist, return a new blank cheat sheet.
  if not os.path.isfile(fname):
    warnings.warn('no cheatsheet file found', UserWarning)
    return sjb.cs.classes.CheatSheet(source_fname=fname)

  json_file = open(fname)
  ob = json.load(json_file)['cheatsheet']
  modified_date = ob['modified_date'] if 'modified_date' in ob else None


  cs = sjb.cs.classes.CheatSheet(
    source_fname=fname, modified_date=modified_date)
  for entry_json in ob['entries']:
    entry = _decode_entry(entry_json)
    cs.add_item(entry, initial_load=True)

  return cs
