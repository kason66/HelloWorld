from sqlalchemy import Table

from flaskr.db import get_db, Base, metadata


class Comment(Base):
    __table__ = Table('comments', metadata, autoload=True)

    def __init__(self, author_id, comment, post_id):
        self.author_id = author_id
        self.comment = comment
        self.post_id = post_id

    @staticmethod
    def get_comments():
        con = get_db()
        comments = con.execute(
            'SELECT c.id, author_id, username, comment, createdTime, post_id '
            'FROM comments c JOIN user u ON c.author_id = u.id'
        ).fetchall()

        return comments

    def get_comment(self):
        con = get_db()
        comment = con.execute(
            'SELECT * FROM comments WHERE post_id = ? AND author_id = ? '
            'ORDER BY createdTime DESC', (self.post_id, self.author_id)
        ).fetchone()

        return comment

    def insert(self):
        con = get_db()
        try:
            con.execute(
                'INSERT INTO comments (post_id, comment, author_id)'
                ' VALUES (?, ?, ?)', (self.post_id, self.comment, self.author_id)
            )
        except BaseException:
            con.rollback()
            raise
        else:
            con.commit()
        return

