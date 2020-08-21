import os
from datetime import timedelta

from flask import Flask
from werkzeug.middleware.shared_data import SharedDataMiddleware


def create_app(test_config=None):  # 应用工厂函数
    # create and configure the app
    # __name__是当前Python模块的名称，告诉应用当前工作路径
    # instance_relative_config=Ture告诉应用，配置文件是相对于instance文件夹的相对路径
    app = Flask(__name__, instance_relative_config=True)
    db_file = 'flaskr.sqlite'
    app.config.from_mapping(
        SECRET_KEY='dev',
        JSONIFY_PRETTYPRINT_REGULAR=True,  # jsonify响应会输出新行、空格和缩进以便于阅读。在调试模式下总是启用的。
        DATABASE=os.path.join(app.instance_path, db_file),
        SQLALCHEMY_DATABASE_URI='/'.join(('sqlite://', app.instance_path, db_file)),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'upload'),
        ALLOWED_EXT={'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}
    )
    # 设置浏览器缓存文件时间，设置为1秒可以快速更新静态文件
    app.send_file_max_age_default = timedelta(seconds=1)

    # 设置jinja的行语句前缀和行注释前缀
    app.jinja_env.line_statement_prefix = "#"
    app.jinja_env.line_comment_prefix = "##"
    # 去掉jinja渲染后块语句所在的空行
    # app.jinja_env.trim_blocks = True
    # app.jinja_env.lstrip_blocks = True

    # test os.path.join()
    # app.logger.warning(app.config.get('DATABASE'))
    # print('app.instance_path:%s\nconfig-DATABASE:%s\nconfig-SQLALCHEMY_DATABASE_URI:%s' % (
    #     app.instance_path, app.config.get('DATABASE'), app.config.get('SQLALCHEMY_DATABASE_URI')))

    if test_config is None:
        # load the instance config, if it exits, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that say hello
    @app.route('/hello')
    def hello():
        return 'Hello World!'

    # 注册数据库到app
    from . import db
    db.init_app(app)

    # 注册auth蓝图到app
    from . import auth
    app.register_blueprint(auth.bp)

    # 注册blog蓝图到app
    from . import blog
    app.register_blueprint(blog.bp)
    # Set this to True and the rule will never match but will create a URL that can be build.
    app.add_url_rule('/uploads/<filename>', endpoint='show_photo', build_only=True)
    # One can also mount files on the root folder and still continue to use the application because the shared data
    # middleware forwards all unhandled requests to the application,
    # even if the requests are below one of the shared folders.
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/show_photo': app.config['UPLOAD_FOLDER']
    })

    from markupsafe import Markup

    # 注册一个模版过滤器，用于生成js脚本Date.toLocaleString()转换GMT时间为客户端本地格式的本地时间
    @app.template_filter("toLocaleString")
    def to_locale_string(datatime):
        return Markup("<script>document.write(new Date({}).toLocaleString());</script>".format(datatime))
    return app


