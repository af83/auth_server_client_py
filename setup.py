from setuptools import setup

PACKAGE = 'AuthServerClient'
VERSION = '0.0.3'

additional_requires = []
try:
  import json
except ImportError:
  additional_requires.append('simplejson>=2.1.2')

setup(
  name=PACKAGE,
  version=VERSION,
  description='AuthServer client lib',
  keywords='authserver oauth2 authentication authorization wsgi middleware',
  license='AGPL v3',
  author='Pierre Ruyssen (AF83)',
  author_email='pierre@ruyssen.eu',
  url='https://github.com/AF83/auth_server_client_py',
  packages=['auth_server_client'],
  include_package_data = True,
  test_suite='nose.collector',
  package_data={},
  install_requires = [] + additional_requires,
  extras_require = {'test' : ['nose==1.0.0']},
  dependency_links=[],
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Programming Language :: Python",
    "Topic :: Internet :: WWW/HTTP :: WSGI",
    "Topic :: Software Development :: Libraries :: Python Modules",
  ],
)

