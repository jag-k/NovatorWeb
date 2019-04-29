from pprint import pprint

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
@admin_route("/", method=[GET, POST])
def admin_page():
    alert = None
    if request.method == POST:
        files = []
        for file in request.files.values():   # type: bottle.FileUpload
            file.save("./public/images/" + file.raw_filename, True)
            files.append(file.raw_filename)
        return redirect("/admin", alert=Alert("Файл(ы) (%s) успешно сохранен(ы)" % ', '.join(files)))
    return admin_temp(
        "main",
        alert=alert
    )


"""BLOG"""
BLOG_POSTS = 7


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
    dump(posts, open(POSTS_FILE, 'w'), ensure_ascii=False, indent=2)
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

        if params.get('del_image'):
            res['img'] = None

        elif not files:
            res['img'] = post.get('img')

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

        if not files or params.get('del_image'):
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


"""NOVATOR"""
DOC_TYPES = {
    'pdf': 'pdf',
    'zip': 'archive',
    'msword': 'word',
    'vnd.openxmlformats-officedocument.wordprocessingml.document': 'word'
}


@admin_route('/novatorweb')
def admin_novator():
    return admin_temp('novator', "NovatorWEB", directions=directions, competition=competition, timer=timer)


@admin_route('/novatorweb/delete')
def delete_direction():
    direction_id = request.query.id
    direction_ids = list(map(lambda x: x["name"], directions))
    if not direction_id or direction_id not in direction_ids:
        alert = Alert("Такого направления не существует", Alert.DANGER)
        return redirect('/admin/novatorweb', alert=alert)

    del directions[direction_ids.index(direction_id)]
    dump(directions, open(DIRECTIONS_FILE, 'w'), ensure_ascii=False, indent=2)
    return redirect('/admin/novatorweb', alert=Alert("Направление успешно удалено"))


@admin_route('/novatorweb/new', method=[GET, POST])
def new_direction():
    if request.method == POST:
        params = dict(request.params)
        if params['name'] in map(lambda x: x["name"], directions):

            return redirect('/admin/novatorweb/new', alert=Alert(
                "Направление с таким именем (%s) уже существует! Попробуйте другое" % params['name'],
                Alert.DANGER
            ))
        res = {"name": params['name'], 'video': params.get('video') or None}
        print(res)
        files = dict(request.files)  # type: Dict[str, bottle.FileUpload]
        img, doc = files.get('image'), files.get('doc')

        if not img or params.get('del_image'):
            res['img'] = None

        else:
            image_name = params['name'] + '.' + img.filename.rsplit('.', 1)[-1]
            img.save('./public/images/novator/' + image_name, True)

            res['img'] = image_name

        if params.get('video'):
            res['video'] = params.get('video')

        doc_name = params['name'] + '.' + doc.filename.rsplit('.', 1)[-1]
        doc.save('./public/novator/' + doc_name, True)
        res['doc'] = doc_name
        res['doc_type'] = DOC_TYPES.get(doc.content_type.split('/')[-1], 'alt')

        directions.append(res)
        dump(directions, open(DIRECTIONS_FILE, 'w'), ensure_ascii=False, indent=2)
        return redirect('/admin/novatorweb', alert=Alert('Направление успешно создано!'))

    return admin_temp('new_direction', "Новое направление")


@admin_route("/novatorweb/edit", method=[GET, POST])
def edit_direction():
    direction_id = request.query.id
    direction_ids = list(map(lambda x: x["name"], directions))

    if not direction_id or direction_id not in direction_ids:
        alert = Alert("Такого направления не существует", Alert.DANGER)
        return redirect('/admin/novatorweb', alert=alert)

    direction = directions[direction_ids.index(direction_id)]

    if request.method == POST:
        params = dict(request.params)
        res = {"name": params['name']}
        files = dict(request.files)  # type: Dict[str, bottle.FileUpload]
        img, doc = files.get('image'), files.get('doc')

        if params.get('del_image'):
            res['img'] = None

        elif not img:
            res['img'] = direction.get('img')

        else:
            image_name = params['name'] + '.' + img.filename.rsplit('.', 1)[-1]
            img.save('./public/images/novator/' + image_name, True)
            res['img'] = image_name

        if doc:
            doc_name = params['name'] + '.' + doc.filename.rsplit('.', 1)[-1]
            doc.save('./public/novator/' + doc_name, True)
            res['doc'] = doc_name
            res['doc_type'] = DOC_TYPES.get(doc.content_type.split('/')[-1], 'alt')
        else:
            res['doc'] = direction.get('doc')
            res['doc_type'] = direction.get('doc_type')

        if params.get('video', direction.get('video')):
            res['video'] = params.get('video', direction.get('video'))

        directions[direction_ids.index(direction_id)] = res
        dump(directions, open(DIRECTIONS_FILE, 'w'), ensure_ascii=False, indent=2)
        return redirect('/admin/novatorweb',
                        alert=Alert('Направление "%s" успешно отредактировано!' % direction['name']))

    return admin_temp('new_direction', "Редактирование направления", direction=direction)


@admin_route('/novatorweb/competition', method=POST)
def admin_competition():
    file = request.files.get('doc')  # type: bottle.FileUpload
    name = 'Положение' + '.' + file.filename.rsplit('.', 1)[-1]
    file.save('./public/' + name, True)
    competition['type'] = DOC_TYPES.get(file.content_type.split('/')[-1], 'alt')
    competition['name'] = name
    dump(competition, open(COMPETITION_FILE, 'w'), ensure_ascii=False, indent=2)
    return redirect('/admin/novatorweb', alert=Alert("Положение успешно загруженно!"))


@admin_route('/novatorweb/timer', method=POST)
def novator_timer():
    data = request.params  # type: bottle.FormsDict
    if data.get('date'):
        timer['endYear'], timer['endMonth'], timer['endDay'] = map(int, data.get('date').split('-'))
        timer['raw_date'] = data.get('date')

    if data.get('time'):
        timer['endHour'], timer['endMinutes'] = map(int, data.get('time').split(':'))
        timer['raw_time'] = data.get('time')

    pprint(timer)
    dump(timer, open(TIMER_FILE, 'w'), ensure_ascii=False, indent=2)
    return redirect('/admin/novatorweb',
                    alert=Alert(
                        "Таймер успешно установлен установлен на "
                        "%(endDay)s-%(endMonth)s-%(endYear)s %(endHour)s:%(endMinutes)s" % timer
                    ))


@admin_route('/novatorweb/reset_timer')
def novator_reset_timer():
    global timer
    timer = {}
    dump(timer, open(TIMER_FILE, 'w'), ensure_ascii=False, indent=2)
    return redirect('/admin/novatorweb',
                    alert=Alert(
                        "Таймер успешно сброшен"
                    ))


# #   MAIN   # #
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


@route('/novatorweb')
def novator():
    return template('novatorweb', "NovatorWEB", directions=directions, competition=competition, timer=timer)


@route('/novatorweb/<direction_id>')
def novator_direction(direction_id):
    direction_ids = list(map(lambda x: x["name"], directions))

    if not direction_id or direction_id not in direction_ids:
        alert = Alert("Такого направления не существует", Alert.DANGER)
        return redirect('/novatorweb', alert=alert)
    direction = directions[direction_ids.index(direction_id)]
    return template('novator_direction', direction['name'] + " (NowatorWEB)", **direction)


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
    f = bottle.static_file(file, "./public")
    if f.status_code == 404:
        return bottle.HTTPError(404, "Страница или файл '/%s' не найдена!" % file)
    return f


if __name__ == '__main__':
    bottle.run(app=app, host="0.0.0.0", port=80, quiet=False, reloader=True)
