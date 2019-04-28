# /usr/bin/python3
from functools import wraps
from os.path import join
from hashlib import pbkdf2_hmac
from sys import stderr
import binascii
from typing import Dict, List

import bottle
from bottle import response, request

try:
    from ujson import load, dump, loads, dumps
except ImportError:
    print("Please, install ujson module (pip3 install ujson)", file=stderr)
    from json import load, dump, loads, dumps

GET, POST, DELETE, PATCH = "GET", "POST", "DELETE", "PATCH"
app = bottle.Bottle()
bottle.ERROR_PAGE_TEMPLATE = open("view/error.html").read()


class Alert:
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"

    def __init__(self, content: str, alert_type=SUCCESS):
        self.content = content
        self.alert_type = alert_type

    @property
    def conv(self):
        return {
            "content": self.content,
            "type": self.alert_type
        }

    def __dir__(self):
        return {
            "content": self.content,
            "type": self.alert_type
        }

    def __str__(self):
        return 'Alert(%s): "%s"' % (self.alert_type.capitalize(), self.content)

    def __repr__(self):
        return "<Alert(%s) %.10s>" % (self.alert_type.capitalize(), self.content)


# #   ADMINS   # #
def hash_admin(login, pwd, *args, **kwargs):
    dk = pbkdf2_hmac(hash_name='sha256',
                     password=bytes("%s ---- %s" % (login, pwd), 'utf-8'),
                     salt=b'lorem fucking {login} ipsum! 1000-list-nick',
                     iterations=100000)
    return str(binascii.hexlify(dk), encoding="utf-8")


def is_admin(login, pwd, *args, **kwargs):
    return hash_admin(login, pwd) in map(lambda x: x['hash'], ADMINS)


def is_hash_admin(h):
    return h in map(lambda x: x['hash'], ADMINS)


ADMINS_FILE = './data/admins.json'
ADMINS = load(open(ADMINS_FILE))  # type: List[Dict[str, str]]
for i in ADMINS:
    i['hash'] = hash_admin(**i)
dump(ADMINS, open(ADMINS_FILE, 'w'), indent=2)

ADMIN_LOGIN_ROUTE = "/login"
ADMIN_COOKIE_KEY = "user"
ADMIN_COOKIE_SECRET = "adminSecretForNowator"


def admin_route(url, method="GET"):
    def _(func):
        @route("/admin" + url.rstrip("/"), method)
        def wrapped(*args, **kwargs):
            user = request.get_cookie(ADMIN_COOKIE_KEY, None, ADMIN_COOKIE_SECRET)
            if is_hash_admin(user):
                return func(*args, **kwargs)
            bottle.redirect(ADMIN_LOGIN_ROUTE + "?from=/admin" + url.rstrip("/"))
        return wrapped
    return _


def admin_temp(source, title="", extension=".html", *args, **kwargs):
    return template(join("admin", source), title + " (Админка)" if title else "Админка", extension, *args, **kwargs)


# #   BLOG   # #
POSTS_FILE = "data/posts.json"
posts = load(open(POSTS_FILE))  # type: List[Dict[str, str]]


# #   MAIN   # #
def template(source, template_title="", extension=".html", including_page=None,
             alert: Alert = None, *args, **kwargs):
    d = loads(request.get_cookie("kwargs", "{}", ADMIN_COOKIE_SECRET))
    if alert:
        alert = alert.conv
    if d:
        response.delete_cookie("kwargs", path='/')
        if 'alert' in d:
            alert = loads(d['alert'])
        kwargs.update(d)
    return bottle.template("view/skeleton.html", title=template_title,
                           is_admin=is_hash_admin(request.get_cookie(ADMIN_COOKIE_KEY, None, ADMIN_COOKIE_SECRET)),
                           including_page=including_page or join("view", source + extension),
                           args=args, alert=alert, kwargs=kwargs)


@wraps(bottle.redirect)
def redirect(url, code=None, alert: Alert = None, **kwargs):
    if kwargs or alert:
        if alert:
            kwargs['alert'] = dumps(alert.conv)
        response.set_cookie("kwargs", dumps(kwargs), ADMIN_COOKIE_SECRET, path='/')
    return bottle.redirect(url, code)


@wraps(bottle.Bottle.route)
def route(p=None, method='GET', callback=None, name=None,
          apply=None, skip=None, **config):

    def _(func):
        app.route(p, method, callback, name,
                  apply, skip, **config)(func)

        path = (p + '/').replace('//', '/')
        app.route(path, method, callback, name,
                  apply, skip, **config)(func)
        return func
    return _

