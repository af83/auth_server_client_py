from setuptools import setup

PACKAGE = 'AuthServerClient'
VERSION = '0.0.1'

additional_requires = []
try:
  import json
except ImportError:
  additional_requires.append('simplejson==2.1.2')

setup(
  name=PACKAGE,
  version=VERSION,
  description='AuthServer client lib',
  license='AGPL 3',
  author='Pierre Ruyssen (AF83)',
  author_email='pierre@ruyssen.fr',
  url='',
  packages=['auth_server_client'],
  include_package_data = True,
  package_data={},
  install_requires = [
    'nose==1.0.0',
  ] + additional_requires,
)

