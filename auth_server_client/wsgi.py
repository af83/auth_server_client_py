
import webob

from auth_server_client import oauth2
from auth_server_client import utils


class AuthMiddleware(object):
  """WSGI AuthServer client middleware.

  The WSGI environ is expected to contain the following keys:
    - beaker.session: a beaker session object where will be read/set:
      - user
      - token

  """

  def __init__(self, app):
    self.app = app

  def __call__(self, environ, start_response):
    request = webob.Request(environ)
    if request.path == oauth2.LOGIN_PATH:
      return self.login(request, environ, start_response)
    elif request.path == oauth2.LOGOUT_PATH:
      return self.logout(request, environ, start_response)
    elif request.path == oauth2.PROCESS_PATH:
      return self.process(request, environ, start_response)
    else:
      return self.app(environ, start_response)

  def login(self, request, environ, start_response):
    # Redirect the user to auth_server for login:
    url = oauth2.get_login_url()
    start_response('302 Redirect', [('Location', url)])
    return ['']

  def logout(self, request, environ, start_response):
    # Reset the session
    session = environ['beaker.session']
    session.pop('user', None)
    session.save()
    start_response('302 Redirect', [('Location', '/')])
    return ['']

  def process(self, request, environ, start_response):
    code = request.GET.get('code')
    # TODO: if not code: abort(401)

    try:
      access_token = oauth2.process_code(code)
    except ValueError:
      start_response('400 Bad request', [])
      return ['']

    if access_token is None:
      start_response('401 Unauthorized', [])
      return ['']

    try:
      info = oauth2.get_authorizations(access_token)
    except ValueError, err:
      start_response('500 Internal Server Error', [])
      return ['%s' % err]

    # Keep the info in session:
    session = environ['beaker.session']
    session['user'] = info
    token = session['token'] = utils.get_random_token()
    session.save()

    start_response('302 Redirect', [('Location', '/')])
    return ['']

