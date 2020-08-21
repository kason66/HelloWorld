from sqlalchemy import Table

from flaskr.db import get_db, metadata, Base


class Img(Base):
    __table__ = Table('imgs', metadata, autoload=True)

    def __init__(self, name, url):
        self.name = name
        self.url = url

    @staticmethod
    def get_imgs():
        con = get_db()
        imgs = con.execute('SELECT * FROM imgs').fetchall()

        return imgs




