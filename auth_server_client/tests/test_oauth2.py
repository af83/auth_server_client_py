# -*- coding: utf-8 -*-
from __future__ import with_statement

from StringIO import StringIO
from unittest import TestCase
import urllib

from auth_server_client import oauth2


class InitTest(TestCase):

  args = ['client_id', 'redirect_uri', 'client_secret', 'authorize_url',
          'token_url', 'auths_url', 'login_path', 'logout_path',
          'process_path']

  def test_init_optionals(self):
    # Without specifying the optinal args:
    oauth2.init(*self.args[:-3])
    self.assertEqual([oauth2.CLIENT_ID, oauth2.REDIRECT_URI, 
                      oauth2.CLIENT_SECRET, oauth2.AUTHORIZE_URL,
                      oauth2.TOKEN_URL, oauth2.AUTHS_URL, 
                      oauth2.LOGIN_PATH, oauth2.LOGOUT_PATH,
                      oauth2.PROCESS_PATH],
                     self.args[:-3] + [None, None, None])

  def test_init_nooptionals(self):
    # Specifying the optional args:
    oauth2.init(*self.args)
    self.assertEqual([oauth2.CLIENT_ID, oauth2.REDIRECT_URI, 
                      oauth2.CLIENT_SECRET, oauth2.AUTHORIZE_URL,
                      oauth2.TOKEN_URL, oauth2.AUTHS_URL, 
                      oauth2.LOGIN_PATH, oauth2.LOGOUT_PATH,
                      oauth2.PROCESS_PATH], self.args)


class GetLoginURLTest(TestCase):

  def setUp(self):
    oauth2.CLIENT_ID = "clientid"
    oauth2.REDIRECT_URI = "http://me/oauth2/process"
    oauth2.AUTHORIZE_URL = "http://authserver/oauth2/auth"

  def test_no_state(self):
    url = oauth2.get_login_url()
    self.assertEqual(url, ("http://authserver/oauth2/auth?"
                           "redirect_uri=http%3A%2F%2Fme%2Foauth2%2Fprocess&"
                           "response_type=code&client_id=clientid"))

  def test_state(self):
    url = oauth2.get_login_url("somestate")
    self.assertEqual(url, ("http://authserver/oauth2/auth?state=somestate&"
                           "redirect_uri=http%3A%2F%2Fme%2Foauth2%2Fprocess&"
                           "response_type=code&client_id=clientid"))


class URLOpenTest(TestCase):
  
  def fake_urlopen(self, url, qs=None):
    """Assert args equal to self.furlopen_{url, qs} + return/raise furlopen_result.
    """
    self.assertEqual(self.furlopen_url, url)
    self.assertEqual(self.furlopen_qs, qs)
    result = self.furlopen_result
    if isinstance(result, Exception):
      raise result
    return result


class ProcessCodeTest(URLOpenTest):
  
  def setUp(self):
    oauth2.TOKEN_URL = "http://authserver/token"
    oauth2.CLIENT_ID = "clientid"
    oauth2.REDIRECT_URI = "http://me/oauth2/process"
    oauth2.AUTHORIZE_URL = "http://authserver/oauth2/auth"
    oauth2.CLIENT_SECRET = "somesecret"
    self.furlopen_url = "http://authserver/token"
    self.furlopen_qs = ("client_secret=somesecret&code=code&"
                        "grant_type=authorization_code&"
                        "client_id=clientid&"
                        "redirect_uri=http%3A%2F%2Fme%2Foauth2%2Fprocess")
    self.original_urlopen = urllib.urlopen
    urllib.urlopen = self.fake_urlopen

  def tearDown(self):
    urllib.urlopen = self.original_urlopen

  def test_ioerror(self):
    # IOError while making http request
    self.furlopen_result = IOError('No internet')
    self.assertRaises(ValueError, oauth2.process_code, 'code')

  def test_invalid_json(self):
    # Answer is invalid json
    self.furlopen_result = StringIO('invalid json')
    self.assertRaises(ValueError, oauth2.process_code, 'code')

  def test_no_access_token(self):
    # There is no access_token in answer
    self.furlopen_result = StringIO('{"error": {"message": "err msg"}}')
    self.assertRaises(AssertionError, oauth2.process_code, 'code')

  def test_right_answer(self):
    # AuthServer answer with access_token (correct format)
    self.furlopen_result = StringIO('{"access_token": "sometoken"}')
    token = oauth2.process_code('code')
    self.assertEqual(token, "sometoken")


class GetAuthorizationsTest(URLOpenTest):

  def setUp(self):
    oauth2.AUTHS_URL = "http://authserver/auth"
    self.furlopen_url = "http://authserver/auth?oauth_token=token"
    self.furlopen_qs = None
    self.original_urlopen = urllib.urlopen
    urllib.urlopen = self.fake_urlopen

  def tearDown(self):
    urllib.urlopen = self.original_urlopen

  def test_ioerror(self):
    self.furlopen_result = IOError('No internet')
    self.assertRaises(ValueError, oauth2.get_authorizations, 'token')

  def test_invalid_json(self):
    self.furlopen_result = StringIO('invalid JSON')
    self.assertRaises(ValueError, oauth2.get_authorizations, 'token')
  
  def test_ok(self):
    self.furlopen_result = StringIO('{"email": "toto"}')

