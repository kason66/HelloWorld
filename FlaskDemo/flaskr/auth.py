import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    jsonify, json)
from werkzeug.security import check_password_hash

from .models.Users import User
# from .util import print_url

# 创建名为auth的蓝图,url前缀为/auth
bp = Blueprint('auth', __name__, url_prefix='/auth')


# 注册用户
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method.upper() == 'POST':
        user = User(request.form['username'], request.form['password'])
        error = None

        # 验证用户名和密码是否为空
        if not user.username:
            error = 'Username is required.'
        elif not user.password:
            error = 'Password is required.'
        elif user.get_user() is not None:
            error = 'User {} is already registered.'.format(user.username)

        if error is None:
            user.insert()
            flash(u'Register Success, Please login!')
            return redirect(url_for('auth.login'))

        flash(error, 'error')

    return render_template('auth/register.html')


# 用户登陆
@bp.route('/login', methods=('GET', 'POST'))
def login():

    if request.method.upper() == 'POST':
        log_user = User(request.form['username'], request.form['password'])
        error = None

        user = log_user.get_user()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], log_user.password):
            error = 'Incorrect password.'

        if error is None:
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.html')


# 修改密码
@bp.route('/forget', methods=('GET', 'POST'))
def forget():

    if request.method.upper() == 'POST':
        log_user = User(request.form['username'], request.form['password'])
        error = None

        user = log_user.get_user()

        if user is None:
            error = 'Incorrect username.'

        if error is None:
            log_user.update()
            flash(u'Password changed successfully, Please login!')
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/forget.html')


# 在视图函数处理请求前载入当前用户的信息
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.get_users(user_id=user_id)


# 注销用户
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# 其他试图检查用户是否登陆用
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # print_url()
        if g.user is None:
            session['before_request_path'] = request.path
            # 未登陆重定向前保存Post请求的json格式参数(如果有)
            if len(request.data) != 0:
                for k, v in json.loads(request.data).items():
                    session[k] = v
            # 如果是HttpXMLRequest请求,返回给前端首页URL地址前进行JSON格式化
            if request.environ.get('HTTP_XHR') in ("True",):
                return jsonify({"url": url_for('auth.login')})
            else:
                return redirect(url_for('auth.login'))
        elif session.get("before_request_path"):
            session.pop("before_request_path")
        return view(**kwargs)
    return wrapped_view



