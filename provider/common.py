import os
import math
import base64
import logging
import dbsetup
import constants
import web
import smtplib
from models.users import Users
from models.subscriptions import Subscriptions
from models.applications import Applications
from models.authorization_codes import AuthorizationCodes
from models.bearer_tokens import BearerTokens
from models.email_loopback import EmailLoopback

log = logging.getLogger('pages')

def b64_url_encode(bytes_):
    return base64.b64encode(bytes_, "-_")


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


def sendmail(to_address, subject, body, from_address=constants.FROM_ADDRESS, headers=None, **kw):
    try:
        web.sendmail(from_address, to_address, subject, body, headers=headers, **kw)
    except OSError as e:
        print("Could not send mail.")
        print("OSError: {0}".format(e))
    except smtplib.SMTPServerDisconnected as e:
        print("Server Disconnected.")
        print("SMTPServerDisconnected: {0}".format(e))
    except Exception as e:
        print("Other email error:")
        print("{0.__class__}: {0}, {1}".format(e, e.message))


class ValidationError(Exception):
    pass


class AuthenticationError(Exception):
    pass

# Configure database access
_db = dbsetup.get_db()
users = Users(_db)
subscriptions = Subscriptions(_db)
applications = Applications(_db)
authorization_codes = AuthorizationCodes(_db)
bearer_tokens = BearerTokens(_db)
email_loopback = EmailLoopback(_db)

# Configure template rendering
render = web.template.render(os.path.join(constants.BASE_PATH, 'templates'))


# Configure Sendmail
web.config.smtp_server = constants.config.get('smtp', 'server')
web.config.smtp_port = int(constants.config.get('smtp', 'port',default='587'))
web.config.smtp_username = constants.config.get('smtp', 'username')
web.config.smtp_password = constants.config.get('smtp', 'password')
web.config.smtp_starttls = constants.config.get('smtp', 'starttls').lower() == 'true'


# Configure session storage. Session variable is filled in from server.py
# setting cookie_domain breaks local testing:
# web.config.session_parameters['cookie_domain'] = uri_authority
web.config.session_parameters['cookie_path'] = "/"
session_store = web.session.DBStore(_db, 'sessions')
session = None
