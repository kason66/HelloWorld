from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    jsonify, json, session, current_app, send_from_directory)

from flaskr.auth import login_required
from .db import get_db_session
from .models.Imgs import Img
from .models.Posts import Post
from .models.Tags import Tag
from .util import print_url, upload_save

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    print_url()
    # 如果是分页查询则从session中查询出其他筛选条件
    if request.args.get('page'):
        page = int(request.args.get('page'))
        search = session.get('search')
        tag_id = session.get('tag_id')
    else:
        # 如果是条件查询则分页默认显示第1页，并更新session中的筛选条件
        page = 1
        search = request.args.get('search')
        search = search if search and len(search) != 0 else None
        tag_id = request.args.get('tag_id')
        session['search'] = search
        session['tag_id'] = tag_id

    error = None

    # from flaskr.models.Users import get_users_say
    # get_users_say()

    posts = Post.get_posts_sa(search, tag_id, page, 5)
    from .models.Comments import Comment
    comments = Comment.get_comments()
    tags = Tag.get_tags()
    new_posts = []
    for i, post in enumerate(posts.items):
        if post.imgs:
            img = get_db_session().query(Img).filter(Img.id == int(post.imgs)).one()
        else:
            img = None

        new_post = {
            "id": post.id,
            "title": post.title,
            "author_id": post.author_id,
            "body": post.body,
            "tags_id": post.tags_id,
            "created": post.created,
            "imgs": img,
            "username": post.username,
            "f_author_id": post.f_author_id
        }
        new_posts.append(new_post)

    if posts is None:
        error = 'No any post, Please new one.'

    if error is not None:
        flash(error)
    context = {
        "posts": new_posts,
        "comments": comments,
        "tags": tags,
        "pagination": posts,
        "search": search
    }
    return render_template('blog/index.html', **context)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    tags = Tag.get_tags()
    if request.method.upper() == 'POST':
        if not request.form['title']:
            flash('Title is required.')

        new_tags = []
        for tag in tags:
            if request.values.get(tag['name']):
                new_tags.append(request.values.get(tag['name']))

        filename, file_url = upload_save(request.files, request.url)
        img = Img(filename, file_url)
        db_session = get_db_session()
        db_session.add(img)
        # db_session.flush()
        db_session.commit()
        # img = db_session.query(Img).filter(Img.name == filename and Img.url == file_url).one()

        post = Post(g.user['id'], request.form['title'], request.form['body'], ','.join(new_tags), ','.join((str(img.id),)))

        post.insert()
        return redirect(url_for('blog.index'))

    return render_template('blog/create.html', tags=tags)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(pid):
    post = Post.get_post(pid)
    if post:
        Post.delete(post_id=pid)
    return redirect(url_for('blog.index'))


@bp.route('/<int:pid>/detail', methods=('GET',))
@login_required
def detail(pid):
    post = Post.get_post(pid, False)
    if post:
        tags = Tag.get_tags()
        img = get_db_session().query(Img).filter(Img.id == int(post['imgs'])).one()
        return render_template('blog/detail.html', post=post, tags=tags, img_show=img)
    else:
        return redirect(url_for('blog.index'))


@bp.route('/<int:pid>/update', methods=('GET', 'POST'))
@login_required
def update(pid):
    post = Post.get_post(pid)

    if post:
        tags = Tag.get_tags()
        img = get_db_session().query(Img).filter(Img.id == int(post['imgs'])).one()
        if request.method.upper() == 'POST':
            new_tags = []
            for tag in tags:
                if request.values.get(tag['name']):
                    new_tags.append(request.values.get(tag['name']))
            post = Post(g.user['id'], request.form['title'], request.form['body'], ','.join(new_tags))
            error = None

            if not post.title:
                error = 'Title is required.'

            if error is not None:
                flash(error)
            else:
                post.update(pid)
                return redirect(url_for('blog.index'))

        return render_template('blog/update.html', post=post, tags=tags, img_show=img)
    else:
        return redirect(url_for('blog.index'))


@bp.route('/dofavour/<int:pid>/<string:op>', methods=('GET', ))
@login_required
def dofavour(pid, op):
    if Post.get_post(pid, False):
        from .models.Favours import Favour
        post_favour = Favour(g.user['id'], pid)
        error = None

        if op == 'Like':
            favour = post_favour.get()

            if favour is None:
                post_favour.insert()
            else:
                error = "You had liked the post yet!"
        elif op == 'unLike':
            post_favour.delete()
        else:
            error = "I don't know what you would like to do ."
        flash(error)

    return redirect(url_for('blog.index'))


@bp.route('/dofavour', methods=('GET', 'POST'))
@login_required
def dofavour_js():
    # 处理XMLHttpRequest的Post请求更新页面局部和未登陆重定向的Get请求
    # request.json 只能够接受方法为POST、Body为raw，header内容为application/json类型的数据
    # json.loads(request.dada) 能够同时接受方法为POST、Body为raw，header内容为 Text 或者 application/json类型的值
    op = pid = None
    if request.environ.get('HTTP_XHR') in ("True",):
        if request.method.upper() == 'POST':
            data = json.loads(request.data)
            pid = data['pid']
            op = data['op']

    elif session.get('redirect'):
        pid = session.get('pid')
        op = session.get('op')

    error = None
    result = ""

    if Post.get_post(pid, False):
        from .models.Favours import Favour
        post_favour = Favour(g.user['id'], pid)

        if op == 'Like':
            favour = post_favour.get()

            if favour is None:
                post_favour.insert()
                result = "Like"
            else:
                error = "You had liked the post yet!"
        elif op == 'unLike':
            post_favour.delete()
            result = "unLike"
        else:
            error = "I don't know what you would like to do ."
    else:
        error = "The post id {} is not found.".format(pid)

    # 如果是重定向，返回博客首页
    if session.get('redirect'):
        # session.pop('redirect', None)
        return redirect(url_for('blog.index'))
    else:
        return jsonify({"favour": result, "error": error})


@bp.route('/addComment', methods=('POST',))
@login_required
def comment_add():
    error = None

    if request.method.upper() == 'POST':
        data = json.loads(request.data)
        from .models.Comments import Comment
        comment = Comment(g.user['id'], data['comment_body'], data['pid'])

        if not comment.comment:
            error = 'Comment is required.'
        elif not comment.post_id:
            error = 'Post is not specified.'

        if error is None:
            comment.insert()
            return jsonify({"comment": comment.get_comment()})

    return jsonify({"error": error})


# @bp.route('/upload', methods=('POST', 'GET'))
# def upload_file():
#     if request.method.upper() == 'POST':
#         if 'file' in request.files:
#             flash('No file part.')
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             flash('No file selected.')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(current_app.config['UPLOAD_FOLDER']), filename)
#             return redirect(url_for('show_photo', filename=filename))
#     pass


@bp.route('/show_photo/<filename>')
def show_photo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
