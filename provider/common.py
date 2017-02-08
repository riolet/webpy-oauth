import os
import math
import base64
import ConfigParser
import dbsetup
import constants
import web
from models.users import Users
from models.subscriptions import Subscriptions
from models.applications import Applications
from models.authorization_codes import AuthorizationCodes
from models.bearer_tokens import BearerTokens
from models.email_loopback import EmailLoopback


def b64_url_encode(bytes):
    return base64.b64encode(bytes, "-_")


def generate_salt(length):
    """
    Generate a cryptographically secure random base64 code of the desired length
    :param length: The desired output string length
    :return: A base64 encoded salt
    """
    # base64 stores 6 bits per symbol but os.urandom gives 8 bits per symbol
    bytes_needed = int(math.ceil(length * 6.0 / 8.0))
    random_bytes = os.urandom(bytes_needed)
    encoded = b64_url_encode(random_bytes)
    return encoded[:length]


def report_init(uri, page, protocol, webinput):
    print(" {page} {protocol} ".format(page=page, protocol=protocol).center(50, '-'))
    print("Reconstructed Uri: {0}".format(uri))
    print("SESSION ID: {0}".format(web.ctx.environ.get('HTTP_COOKIE', 'unknown')))
    print("SESSION KEYS: {0}".format(session.keys()))
    print("SESSION: {0}".format(dict(session)))
    print("WEB INPUT: {0}".format(webinput))
    print("-"*50)
    print("")


def response_from_return(headers, body, status):
    print("response_from_return(...)")
    print("  headers: {0}".format(str(headers)[:50]))
    print("  body: {0}".format(str(body)[:50]))
    print("  status: {0}".format(status))
    # raise web.HTTPError(status, headers, body)
    raise web.HTTPError('200 OK', headers, body)


def response_from_error(e):
    raise web.BadRequest('<h1>Bad Request</h1><p>Error is: {0}</p>'.format(e.description))


def sendmail(to_address, subject, body, from_address="info@riolet.com", headers=None, **kw):
    try:
        web.sendmail(from_address, to_address, subject, body, headers=headers, **kw)
    except OSError as e:
        print("Could not send mail.")
        print("OSError: {0}".format(e))


class ValidationError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class SeeOther(web.Redirect):
    def __init__(self, url, absolute=False):
        if url[0] == '/':
            url = uri_prefix + url
            absolute = True
        if constants.DEBUG:
            print("Redirecting (see other) to {0}".format(url))

        web.Redirect.__init__(self, url, '303 See Other', absolute=absolute)

web.seeother = SeeOther


# Configure database access
_db = dbsetup.get_db()
users = Users(_db)
subscriptions = Subscriptions(_db)
applications = Applications(_db)
authorization_codes = AuthorizationCodes(_db)
bearer_tokens = BearerTokens(_db)
email_loopback = EmailLoopback(_db)

# Configure session storage. Session variable is filled in from server.py
session_store = web.session.DBStore(_db, 'sessions')
session = None

# Configure template rendering
render = web.template.render(os.path.join(constants.BASE_PATH, 'templates'))

config = ConfigParser.SafeConfigParser()

# read the defaults, then overwrite that with anything in config
config.read([os.path.join(constants.BASE_PATH, 'config.default'),
             os.path.join(constants.BASE_PATH, 'config')])

# Configure Sendmail
web.config.smtp_server = config.get('smtp', 'server')
web.config.smtp_port = int(config.get('smtp', 'port'))
web.config.smtp_username = config.get('smtp', 'username')
web.config.smtp_password = config.get('smtp', 'password')
web.config.smtp_starttls = config.get('smtp', 'starttls').lower() == 'true'

# Configure path
# This is defined for crafting absolute paths because relative
# redirects using web.seeother() were giving ugly URIs like
# "https://example.com/wsgipython.py/login"
uri_scheme = config.get('domain', 'uri_scheme')
uri_authority = config.get('domain', 'uri_authority')
uri_prefix = "{0}://{1}".format(uri_scheme, uri_authority)