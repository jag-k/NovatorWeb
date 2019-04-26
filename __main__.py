import math

from lib import *
from markdown import markdown


# #   ADMIN ROUTING   # #
@admin_route("/")
def admin_page():
    return admin_temp(
        "main",
        title="Админка",
    )


@admin_route('/blog/new', ["GET", "POST"])
def new_post():
    if request.method == "POST":
        params = dict(request.params)
        if params['title'] in map(lambda x: x["title"], posts):
            return redirect('/admin/blog/new', alert={
                "content": "Пост в блоге с таким заголовком (%s) уже существует! Попробуйте другой" % params['title'],
                "type": "danger"
            })
        res = {"title": params['title']}
        files = dict(request.files)  # type: Dict[str, bottle.FileUpload]

        if not files:
            res['img'] = None

        else:
            file = files['image']
            file.name: str
            print(file.filename)
            filename = params['title'] + '.' + file.filename.rsplit('.', 1)[-1]
            file.save('./public/images/' + filename, overwrite=True)

            res['img'] = filename

        res['content'] = markdown(params['blog_post'])
        res['short'] = params['blog_post'].split('.')[0]

        posts.append(res)
        dump(posts, open(POSTS_FILE, 'w'), indent=2)

        return redirect('/admin', alert={
            "content": "Пост успешно создан!",
            "type": "success"
        })
    return admin_temp('new_blog', "Новый пост в блоге")


# #   MAIN   # #
BLOG_POSTS = 7


@route("/")
def main_page():
    return template(
        "main",
        posts=posts,
    )


@route("/blog")
def blog():
    cur_page = request.params.get("page")
    max_pages = len(posts) // BLOG_POSTS + bool(len(posts) % BLOG_POSTS)
    if cur_page is not None and (not (cur_page.isdigit() and int(cur_page) > 0)) or cur_page == "1":
        return redirect('/blog')
    else:
        cur_page = min(int(cur_page or '1'), max_pages)
    p = posts[(cur_page-1)*BLOG_POSTS:cur_page*BLOG_POSTS]
    pagination = {
        "cur_page": cur_page,
        "max_pages": max_pages,
        "displayed_pages": 5
    }

    return template('blog', "Блог", posts=p, pagination=pagination)


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
                    alert=alert,
                    )


@route("/logout")
def logout():
    response.delete_cookie(ADMIN_COOKIE_KEY)
    return redirect("/")


@route("/<file:path>")
def static(file):
    return bottle.static_file(file, "./public")


if __name__ == '__main__':
    bottle.run(app=app, host="0.0.0.0", port=80, quiet=False, reloader=True)
