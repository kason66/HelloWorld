import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, Query
from sqlalchemy.ext.declarative import declarative_base

from flaskr.pagination import paginate

engine = None
metadata = None
Base = None


def get_db_session():
    if 'db_session' not in g:
        g.db_session = scoped_session(sessionmaker(bind=engine))
    return g.db_session


def get_db():
    if 'con' not in g:
        g.con = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # 方法一：将查询结果使用自定义的装饰函数dic_factory处理后转化为字典
        g.con.row_factory = dic_factory
        # g.con.row_factory = sqlite3.Row
        # 方法二：将SQL查询结果SQLite3.Row类型转换为字典
        # d = {}
        # for key, value in zip(Row.keys(), Row) for Row in sqlite3.Rows:
        #     d[key] = value
    return g.con


def close_db(e=None):
    con = g.pop('con', None)

    if con is not None:
        con.close()

    db_session = g.pop('db_session', None)

    if db_session is not None:
        db_session.close()


def init_db():
    con = get_db()

    with current_app.open_resource('schema.sql') as f:
        con.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    # Clear the existing data and create new tables.
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    global engine
    engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'), echo=True)
    # 直接使用engine进行查询，无需ORM
    # print(engine.execute('select * from user where id = :1', [1]).first())
    global metadata
    metadata = MetaData(bind=engine)
    global Base
    Base = declarative_base()
    # 绑定paginate方法到Query对象，则session.query()可使用paginate()方法
    Query.paginate = paginate


# 将数据库查询结果由sqlite3.row类型转换为字典
def dic_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

