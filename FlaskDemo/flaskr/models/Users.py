from werkzeug.security import generate_password_hash

from flaskr.db import get_db, metadata, Base, get_db_session
from sqlalchemy import Table
from sqlalchemy.orm import Mapper


# 映射方式二：经典映射方式
# user = Table('user', metadata,
#              Column('id', Integer, primary_key=True, autoincrement=True),
#              Column('username', TEXT, unique=True, nullable=False),
#              Column('password', TEXT, nullable=False)
#              )
# Mapper(User, user)


class User(Base):
    # 映射方式一：映射到已有的表，自动检测表字段
    __table__ = Table('user', metadata, autoload=True)

    # 映射方式三：描述要映射的表名和列，__tablename__、Column
    # __tablename__ = 'user'
    #
    # id = Column(Integer, primary_key=True, autoincrement=True)
    # username = Column(TEXT, unique=True, nullable=False)
    # password = Column(TEXT, nullable=False)

    def __init__(self, name, password):
        self.username = name
        self.password = password

    # def __repr__(self):
    #     print('id:{},name:{},password:{}'.format(self.id, self.username, self.password))

    def get_user(self):
        con = get_db()

        if self.username is not None:
            users = con.execute(
                'SELECT * FROM user WHERE username = ?', (self.username,)
            ).fetchone()

        return users

    @staticmethod
    def get_users(user_id=None):
        con = get_db()
        if user_id is None:
            users = con.execute('SELECT * FROM user').fetchall()
        else:
            users = con.execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()
        return users

    def insert(self):
        con = get_db()
        try:
            con.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (self.username, generate_password_hash(self.password))
            )
        except BaseException:
            con.rollback()
            raise
        else:
            con.commit()
        return

    def update(self):
        con = get_db()
        try:
            con.execute(
                'UPDATE user SET  password = ? WHERE username = ?',
                (generate_password_hash(self.password), self.username)
            )
        except BaseException:
            con.rollback()
            raise
        else:
            con.commit()
        return


# 测试SQLAlchemy的使用是否成功
def get_users_say():
    for user in get_db_session().query(User).all():
        print('id:{},name:{},password:{}'.format(user.id, user.username, user.password))






