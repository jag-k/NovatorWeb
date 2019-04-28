from lib import *
from markdown import markdown


def blog_short(t):
    r = ""
    write = True
    for letter in t:
        if letter == "<":
            write = False
            continue
        elif letter == ">":
            write = True
            continue
        if write:
            r += letter
    return r


# #   ADMIN ROUTING   # #
@admin_route("/")
def admin_page():
    return admin_temp(
        "main",
        title="Админка",
    )


@admin_route("/blog")
def admin_blog():
    return admin_temp("blog", "Блог", posts=posts)


@admin_route('/blog/delete')
def delete_post():
    post_id = request.query.id
    post_ids = list(map(lambda x: x["title"], posts))
    if not post_id or post_id not in post_ids:
        alert = Alert("Такого поста не существует", Alert.DANGER)
        return redirect('/admin/blog', alert=alert)

    del posts[post_ids.index(post_id)]
    dump(posts, open(POSTS_FILE, 'w'))
    return redirect('/admin/blog', alert=Alert("Пост успешно удалён"))


@admin_route("/blog/edit", method=[GET, POST])
def edit_post():
    post_id = request.query.id
    post_ids = list(map(lambda x: x["title"], posts))

    if not post_id or post_id not in post_ids:
        alert = Alert("Такого поста не существует", Alert.DANGER)
        return redirect('/admin/blog', alert=alert)

    post = posts[post_ids.index(post_id)]

    if request.method == POST:
        params = dict(request.params)
        res = {"title": params['title']}
        files = dict(request.files)  # type: Dict[str, bottle.FileUpload]

        if not files:
            res['img'] = None

        else:
            file = files['image']
            filename = params['title'] + '.' + file.filename.rsplit('.', 1)[-1]
            file.save('./public/images/' + filename, overwrite=True)

            res['img'] = filename

        res['raw_content'] = params['blog_post']
        res['content'] = markdown(params['blog_post'])

        res['short'] = blog_short(res['content'])
        res['short'] = res['short'][:87] + '...' if len(res['short']) >= 90 else res['short']

        posts[post_ids.index(post_id)] = res
        dump(posts, open(POSTS_FILE, 'w'), ensure_ascii=False, indent=2)
        return redirect('/admin/blog', alert=Alert('Пост "%s" успешно отредактирован!' % post['title']))

    return admin_temp('new_blog', "Редактирование поста", post=post)


@admin_route('/blog/new', [GET, POST])
def new_post():
    if request.method == POST:
        params = dict(request.params)
        if params['title'] in map(lambda x: x["title"], posts):

            return redirect('/admin/blog/new', alert=Alert(
                "Пост в блоге с таким заголовком (%s) уже существует! Попробуйте другой" % params['title'],
                Alert.DANGER
            ))
        res = {"title": params['title']}
        files = dict(request.files)  # type: Dict[str, bottle.FileUpload]

        if not files:
            res['img'] = None

        else:
            file = files['image']
            filename = params['title'] + '.' + file.filename.rsplit('.', 1)[-1]
            file.save('./public/images/' + filename, overwrite=True)

            res['img'] = filename

        res['raw_content'] = params['blog_post']
        res['content'] = markdown(params['blog_post'])

        res['short'] = blog_short(res['content'])
        res['short'] = res['short'][:87] + '...' if len(res['short']) >= 90 else res['short']

        posts.append(res)
        dump(posts, open(POSTS_FILE, 'w'), ensure_ascii=False, indent=2)

        return redirect('/admin/blog', alert=Alert(
            "Пост успешно создан!"
        ))
    return admin_temp('new_blog', "Новый пост в блоге")


# #   MAIN   # #
BLOG_POSTS = 7


@route("/")
def main_page():
    return template(
        "main",
        posts=list(reversed(posts))[:2],
    )


@route("/blog")
def blog():
    cur_page = request.query.getunicode("from")
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


@route(ADMIN_LOGIN_ROUTE, method=["GET", "POST"])
def login():
    alert = None
    if request.method == "POST":
        h = hash_admin(**request.params)
        if is_hash_admin(h):
            response.set_cookie(ADMIN_COOKIE_KEY, h, ADMIN_COOKIE_SECRET, max_age=604800, httponly=True)
            redirect_from = request.get_cookie("redirect", "/admin", ADMIN_COOKIE_SECRET)
            return redirect(redirect_from)
        else:
            alert = Alert(
                "Вы ввели не правильный логин или пароль! Повторите снова",
                Alert.DANGER
            )
    if request.params.get("from"):
        response.set_cookie('redirect', request.params.get("from", '/admin'), ADMIN_COOKIE_SECRET)
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
