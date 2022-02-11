"""
Tools for dealing with WikiTree API.
"""

import json
import re
import urllib.parse
import urllib.request


def api_req(**params):
  encoded_params = urllib.parse.urlencode(params)
  resp = urllib.request.urlopen("https://api.wikitree.com/api.php", 
                                data=encoded_params.encode("utf-8"))
  return json.loads(resp.read())

def is_redirect(profile_num_or_id):
  """Lookup a profile by # or id and figure out it is a redirect or not.
  If it is, return the id of the profile it now redirects to."""
  resp = api_req(action="getBio", key=profile_num_or_id)
  # status == 0 is success. On failure, we see things like:
  # status == "Invalid page id"
  if resp[0]["status"] == 0:
    m = re.fullmatch(r"#REDIRECT \[\[(.*)\]\]", resp[0]["bio"])
    if m:
      # Return wikitree_id of profile this is redirected to.
      return m.group(1)
  # If not a redirect, return nothing
  return None
