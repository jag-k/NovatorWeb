# /usr/bin/python3
from functools import wraps
from os.path import join
from hashlib import pbkdf2_hmac
from sys import stderr
import binascii
from typing import Dict, List

import bottle
from bottle import response, redirect, request

try:
    from ujson import load, dump
except ImportError:
    print("Please, install ujson module (pip3 install ujson)", file=stderr)
    from json import load, dump

app = bottle.Bottle()
bottle.ERROR_PAGE_TEMPLATE = open("view/error.html").read()


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


# #   ADMIN ROUTING   # #
ADMIN_LOGIN_ROUTE = "/login"
ADMIN_COOKIE_KEY = "user"
ADMIN_COOKIE_SECRET = "adminSecretForNowator"


def admin_page(route, method="GET"):
    def _(func):
        @app.route("/admin" + route.rstrip("/"), method)
        def wrapped(*args, **kwargs):
            user = request.get_cookie(ADMIN_COOKIE_KEY, None, ADMIN_COOKIE_SECRET)
            if is_hash_admin(user):
                return func(*args, **kwargs)
            bottle.redirect(ADMIN_LOGIN_ROUTE)
        return wrapped
    return _


# #   BLOG   # #
POSTS_FILE = "data/posts.json"
posts = load(open(POSTS_FILE))  # type: List[Dict[str, str]]


@admin_page('/blog/new', ["GET", "POST"])
def new_post():
    if request.method == "POST":
        print(request.params)
        return redirect('/blog')
    return admin_temp('new_blog', "Новый пост в блоге")


# #   MAIN   # #
def template(source, template_title="", extension=".html", skeleton="view/skeleton.html", including_page=None, *args,
             **kwargs):
    return bottle.template(skeleton, title=template_title,
                           is_admin=is_hash_admin(request.get_cookie(ADMIN_COOKIE_KEY, None, ADMIN_COOKIE_SECRET)),
                           including_page=including_page or join("view", source + extension),
                           args=args, kwargs=kwargs)


def admin_temp(source, title="", extension=".html", *args, **kwargs):
    return template(join("admin", source), title, extension, *args, **kwargs)


@route("/")
def main_page():
    return template("main",
                    posts=posts
                    )


@route("/blog")
def blog():
    return template('blog', "Блог", posts=posts)


@route("/blog/<post>")
def blog_post(post=""):
    p = list(filter(lambda x: x['title'] == post, posts))
    if not p:
        return bottle.HTTPError(404, "Пост блога не найден")
    return template('blog_post', p[0]['title'] + " (Блог)", **p[0])


@route("/login", method=["GET", "POST"])
def login():
    alert = {}
    if request.method == "POST":
        h = hash_admin(**request.params)
        if is_hash_admin(h):
            response.set_cookie(ADMIN_COOKIE_KEY, h, ADMIN_COOKIE_SECRET, max_age=604800, httponly=True)
            return redirect("/admin")
        else:
            alert = {
                'content': "Вы ввели не правильный логин или пароль! Повторите снова",
                'type': "danger"
            }
    return template("login",
                    template_title="Вход в админку",
                    alert=alert
                    )


@app.route("/logout")
def logout():
    response.delete_cookie(ADMIN_COOKIE_KEY)
    return redirect("/")


@admin_page("/")
def admin_page():
    return admin_temp("main",
                      title="Админка"
                      )


@route("/<file:path>")
def static(file):
    return bottle.static_file(file, "./public")


if __name__ == '__main__':
    bottle.run(app=app, host="0.0.0.0", port=80, quiet=False, reloader=True)

