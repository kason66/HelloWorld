from sqlalchemy import Table

from flaskr.db import get_db, metadata, Base


class Favour(Base):
    __table__ = Table('favours', metadata, autoload=True)

    def __init__(self, author_id, post_id):
        self.author_id = author_id
        self.post_id = post_id

    def get(self):
        """
        Get the favour record with author_id and post_id in Favour instance.

        :return: one favour or None
        """
        favour = get_db().execute(
            'SELECT * FROM favours WHERE post_id = ? AND author_id = ?', (self.post_id, self.author_id)
        ).fetchone()
        return favour

    def insert(self):
        con = get_db()
        try:
            con.execute(
                'INSERT OR IGNORE INTO favours (post_id, author_id)'
                ' VALUES (?, ?)', (self.post_id, self.author_id)
            )
        except BaseException:
            con.rollback()
            raise
        else:
            con.commit()
        return

    def delete(self):
        con = get_db()
        try:
            con.execute(
                'DELETE FROM favours WHERE post_id = ? AND author_id = ?', (self.post_id, self.author_id)
            )
        except BaseException:
            con.rollback()
            raise
        else:
            con.commit()
        return

