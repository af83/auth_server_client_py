# -*- coding: utf-8 -*-

try:
  import json
except ImportError:
  import simplejson as json
import urllib


CLIENT_ID = None
REDIRECT_URI = None
CLIENT_SECRET = None
AUTHORIZE_URL = None
TOKEN_URL = None
AUTHS_URL = None
AUTHORITY = None
DOMAIN = None

# This is only usefull for middleware:
LOGIN_PATH = None
LOGOUT_PATH = None
PROCESS_PATH = None


def init(client_id, redirect_uri, client_secret, authorize_url, token_url, 
         auths_url, authority, domain,
         login_path=None, logout_path=None, process_path=None):
  """Init module variables.
  """
  global CLIENT_ID, REDIRECT_URI, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, \
         AUTHS_URL, AUTHORITY, DOMAIN, \
         LOGIN_PATH, LOGOUT_PATH, PROCESS_PATH, AUTHS_URL
  CLIENT_ID = client_id
  REDIRECT_URI = redirect_uri
  CLIENT_SECRET = client_secret
  AUTHORIZE_URL = authorize_url
  TOKEN_URL = token_url
  AUTHS_URL = auths_url
  AUTHORITY = authority
  DOMAIN = domain
  
  LOGIN_PATH = login_path
  LOGOUT_PATH = logout_path
  PROCESS_PATH = process_path
  

def get_login_url(state=None):
  """Returns URL to redirect the user to for him to login using AuthServer.

  Arguments:
    - state: string, some state you want to get back when processing 
      the request back.

  """
  args = dict(client_id=CLIENT_ID, response_type="code", 
              redirect_uri=REDIRECT_URI)
  if state is not None: 
    args["state"] = state
  return "%s?%s" % (AUTHORIZE_URL, urllib.urlencode(args))


def process_code(code):
  """Process the code issued by auth_server, returns the access_token.
  The ValueError will be raised if the given code is invalid.
  The AssertionError will be raised if no access_token returned by AuthServer.

  Arguments:
    - code: the OAuth2 code issued by AuthServer and passed through the end-user.

  """
  # XXX: client_secret might have to go in headers (cf. OAuth2 protocol).
  args = dict(client_id=CLIENT_ID, 
              redirect_uri=REDIRECT_URI,
              client_secret=CLIENT_SECRET,
              grant_type= "authorization_code",
              code=code)
  qs = urllib.urlencode(args)
  try:
    res = urllib.urlopen(TOKEN_URL, qs).read()
    data = json.loads(res)
  except (IOError, ValueError):
    raise ValueError('Invalid code')
  if "access_token" not in data:
    raise AssertionError(data.get('error', {}).get('message', ''))
  return data.get('access_token')


def get_authorizations(access_token):
  """Get the authorizations and info associated to the given access_token.
  Will raise a ValueError if invalid response from AuthServer.

  Arguments:
    - access_token: the OAuth2 access_token given by AuthServer.

  """
  # XXX: access token might have to be in headers (cf. OAuth2 protocol).
  querystring = urllib.urlencode({'oauth_token': access_token,
                                  'authority': AUTHORITY,
                                  'domain': DOMAIN})
  url = '%s?%s' % (AUTHS_URL, querystring)
  try:
    res = urllib.urlopen(url).read()
    return json.loads(res)
  except IOError, err:
    raise ValueError('Invalid answer from AuthServer: %s' % err)
  except ValueError, err:
    raise ValueError('Invalid answer from AuthServer: %s\n%s' % (err, res))    

