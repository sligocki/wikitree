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


class RedirectInfo:
  def __init__(self, json_response):
    self.status = json_response[0]["status"]

    # Save Redirection info
    self.redirects_to = None
    if self.status == 0:
      m = re.fullmatch(r"#REDIRECT \[\[(.*)\]\]", json_response[0]["bio"])
      if m:
        self.redirects_to = m.group(1)


def redirect_info(profile_num_or_id):
  """Lookup a profile by # or id and figure out it is a redirect or not.
  If it is, return the id of the profile it now redirects to."""
  resp = api_req(action="getBio", key=profile_num_or_id)
  return RedirectInfo(resp)
