from flask import flash, g
from sqlalchemy import Table
from sqlalchemy.sql.elements import and_

from flaskr.db import get_db, Base, metadata, get_db_session
from flaskr.models.Favours import Favour
from flaskr.models.Users import User


class Post(Base):
    __table__ = Table('post', metadata, autoload=True)

    def __init__(self, author_id, title, body, tags, imgs=None):
        self.author_id = author_id
        self.title = title
        self.body = body
        self.tags = tags
        self.imgs = imgs

    def insert(self):
        con = get_db()
        try:
            con.execute(
                'INSERT INTO post (title, body, author_id, tags, imgs)'
                ' VALUES (?, ?, ?, ?, ?)', (self.title, self.body, self.author_id, self.tags, self.imgs)
            )
        except BaseException:
            con.rollback()
            raise
        else:
            con.commit()
        return

    def update(self, post_id):
        con = get_db()
        try:
            con.execute(
                'UPDATE post SET title = ?, body = ?, tags = ?, imgs = ? WHERE id = ?',
                (self.title, self.body, self.tags, self.imgs, post_id)
            )
        except BaseException:
            con.rollback()
            raise
        else:
            con.commit()
        return None

    @staticmethod
    def get_post(post_id, check_author=True):
        """
        Get a post with the specified post_id, and check if the user is author of post by the check_author default true

        :param post_id: id of the post to get
        :param check_author: check if author of the post is current user with given , Not check if false
        :return: Post with the specified post_id , or false if the post not found or the author is not current user
        """

        sql_select = 'SELECT p.id, title, body, created, p.author_id, username, p.tags as tags_id, p.imgs '
        sql_from_post = 'FROM post p JOIN user u ON p.author_id = u.id and p.id = ? '
        sql_left_outer_join = 'left outer join favours f on f.author_id = ?  and p.id = f.post_id '
        sql = sql_select + ', f.author_id as f_author_id ' + sql_from_post + sql_left_outer_join

        post = get_db().execute(sql, (post_id, g.user['id'])).fetchone()

        if post is None:
            flash(error="Post id {0} doesn't exist.".format(post_id))
            return False

        if check_author and post['author_id'] != g.user['id']:
            flash(error="You have not the permission.")
            return False

        return post

    @staticmethod
    def get_posts(search=None, tags_id=None):
        """
        Get the posts with the specified args and favours if the current user have been logging in .

        :param search: the title of post to search, can be part of the title entity.
        :param tags_id: the tag_id included the post to search.
        :return: the posts with the specified args and favours is the user logging in.
        """
        sql_select = 'SELECT p.id, title, body, created, p.author_id, u.username, p.tags as tags_id, p.imgs '
        sql_from_post = 'FROM post p JOIN user u ON p.author_id = u.id '
        sql_left_outer_join = 'left outer join favours f on f.author_id = ?  and p.id = f.post_id '
        sql_where_tag = 'WHERE p.tags like ? '
        sql_where_search = 'WHERE p.title like ?'
        sql_order_by = 'ORDER BY created DESC '

        if search and tags_id is None:
            if g.user:
                sql = sql_select + ', f.author_id as f_author_id ' + sql_from_post + sql_left_outer_join + \
                      sql_where_search + sql_order_by
                posts = get_db().execute(sql, (g.user['id'], '%' + search + '%')).fetchall()
                return posts
            else:
                sql = sql_select + sql_from_post + sql_where_search + sql_order_by
                posts = get_db().execute(sql, ('%' + search + '%',)).fetchall()
                return posts
        elif search is None and tags_id:
            if g.user:
                sql = sql_select + ', f.author_id as f_author_id ' + sql_from_post + sql_left_outer_join + \
                      sql_where_tag + sql_order_by
                posts = get_db().execute(sql, (g.user['id'], '%'+tags_id+'%')).fetchall()
                return posts
            else:
                sql = sql_select + sql_from_post + sql_where_tag + sql_order_by
                posts = get_db().execute(sql, ('%' + tags_id + '%',)).fetchall()
                return posts
        elif search is None and tags_id is None:
            if g.user:
                sql = sql_select + ', f.author_id as f_author_id ' + sql_from_post + sql_left_outer_join + sql_order_by
                posts = get_db().execute(sql, (g.user['id'],)).fetchall()
                return posts
            else:
                sql = sql_select + sql_from_post + sql_order_by
                posts = get_db().execute(sql).fetchall()
                return posts
        else:
            pass

    @staticmethod
    def get_posts_sa(search=None, tags_id=None, page=None, per_page=None):
        """
        Get the posts with the specified args and favours if the current user have been logging in. Using SQLAlchemy to
        complete the function pagination.

        :param per_page: how many items in per page.
        :param page: which page of total pages to display.
        :param search: the title of post to search, can be part of the title entity.
        :param tags_id: the tag_id included the post to search.
        :return: the posts with the specified args and favours is the user logging in.
        """

        if search and tags_id is None:
            if g.user:
                posts = get_db_session().query(
                    Post.id, Post.title, Post.body, Post.created, Post.author_id, Post.tags.label('tags_id'), Post.imgs,
                    User.username, Favour.author_id.label('f_author_id')).join(User, Post.author_id == User.id). \
                    outerjoin(Favour, and_(Favour.post_id == Post.id, Favour.author_id == g.user['id'])). \
                    filter(Post.title.like('%' + search + '%')).order_by(Post.created.desc()).paginate(page, per_page)
                return posts
            else:
                posts = get_db_session().query(
                    Post.id, Post.title, Post.body, Post.created, Post.author_id, Post.tags.label('tags_id'), Post.imgs,
                    User.username, Favour.author_id.label('f_author_id')).join(User, Post.author_id == User.id).\
                    outerjoin(Favour, and_(Favour.post_id == Post.id, Favour.author_id == 0)).\
                    filter(Post.title.like('%' + search + '%')).order_by(Post.created.desc()).paginate(page, per_page)
                return posts
        elif search is None and tags_id:
            if g.user:
                posts = get_db_session().query(
                    Post.id, Post.title, Post.body, Post.created, Post.author_id, Post.tags.label('tags_id'), Post.imgs,
                    User.username, Favour.author_id.label('f_author_id')).join(User, Post.author_id == User.id). \
                    outerjoin(Favour, and_(Favour.post_id == Post.id, Favour.author_id == g.user['id'])). \
                    filter(Post.tags.like('%'+tags_id+'%')).order_by(Post.created.desc()).paginate(page, per_page)
                return posts
            else:
                posts = get_db_session().query(
                    Post.id, Post.title, Post.body, Post.created, Post.author_id, Post.tags.label('tags_id'), Post.imgs,
                    User.username, Favour.author_id.label('f_author_id')).join(User, Post.author_id == User.id).\
                    outerjoin(Favour, and_(Favour.post_id == Post.id, Favour.author_id == 0)).\
                    filter(Post.tags.like('%'+tags_id+'%')).order_by(Post.created.desc()).paginate(page, per_page)
                return posts
        elif search is None and tags_id is None:
            if g.user:
                posts = get_db_session().query(
                    Post.id, Post.title, Post.body, Post.created, Post.author_id, Post.tags.label('tags_id'), Post.imgs,
                    User.username, Favour.author_id.label('f_author_id')).join(User, Post.author_id == User.id). \
                    outerjoin(Favour, and_(Favour.post_id == Post.id, Favour.author_id == g.user['id'])). \
                    order_by(Post.created.desc()).paginate(page, per_page)
                for post in posts.items:
                    print(post)
                return posts
            else:
                posts = get_db_session().query(
                    Post.id, Post.title, Post.body, Post.created, Post.author_id, Post.tags.label('tags_id'), Post.imgs,
                    User.username, Favour.author_id.label('f_author_id')).join(User, Post.author_id == User.id). \
                    outerjoin(Favour, and_(Favour.post_id == Post.id, Favour.author_id == 0)). \
                    order_by(Post.created.desc()).paginate(page, per_page)
                return posts
        else:
            pass

    @staticmethod
    def delete(post_id=None, check_id=True):
        con = get_db()
        try:
            if check_id and post_id:
                con.execute('DELETE FROM post WHERE id = ?', (post_id,))
            elif check_id is False:
                con.execute('DELETE FROM post')
        except BaseException:
            con.rollback()
            raise
        else:
            con.commit()
        return
