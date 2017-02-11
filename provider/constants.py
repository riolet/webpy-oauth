import os
import ConfigParser

BASE_PATH = os.path.dirname(__file__)

config = ConfigParser.SafeConfigParser()
config.read([os.path.join(BASE_PATH, 'config.default'),
             os.path.join(BASE_PATH, 'config')])

DEBUG = config.get('debug', 'debug').lower() == 'true'

# Used for database access
DB_PATH = os.path.join(BASE_PATH, config.get('db', 'db_path'))
DB_FILENAME = config.get('db', 'db_file')

# used in setting cookies
REMEMBER_COOKIE_NAME = "rememberme"

USE_TLS = config.get('ssl', 'use_ssl').lower() == 'true'

urls = [
    '/', 'pages.account.Account',
    '/login', 'pages.login.Login',
    '/admin', 'pages.admin.Admin',
    '/register', 'pages.register.Register',
    '/subscribe', 'pages.subscribe.Subscribe',
    '/logout', 'pages.logout.Logout',
    '/authorize', 'pages.authorize.Authorize',
    '/token', 'pages.token.Token',
    '/resource', 'pages.resource.Resource',
    '/resetpassword', 'pages.resetpassword.ResetPassword',
    '/changepassword', 'pages.changepassword.ChangePassword',
    '/confirmemail', 'pages.confirmemail.ConfirmEmail'
]
if DEBUG:
    urls.extend(['/_debug_', 'pages.test.Env'])


# Configure paths
# This is defined for crafting absolute paths because relative
# redirects using web.seeother() were giving ugly URIs like
# "https://example.com/wsgipython.py/login"
uri_scheme = config.get('domain', 'base_url')
uri_authority = config.get('domain', 'uri_authority')
uri_prefix = "{0}://{1}".format(uri_scheme, uri_authority)
