from sqlalchemy import Table

from flaskr.db import get_db, metadata, Base


class Tag(Base):
    __table__ = Table('tags', metadata, autoload=True)

    def __init__(self, name, level, parent_id):
        self.name = name
        self.level = level
        self.parent_id = parent_id

    @staticmethod
    def get_tags():
        con = get_db()
        tags = con.execute('SELECT * FROM tags').fetchall()

        return tags



