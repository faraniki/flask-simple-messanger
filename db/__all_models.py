from db.db_session import SqlAlchemyBase
import sqlalchemy as db
import sqlalchemy.orm as orm
from datetime import datetime

class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)

    message = orm.relationship('Message')

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


class Message(SqlAlchemyBase):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=True)
    user_login = db.Column(db.Integer, db.ForeignKey('users.login'))
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'))
    dt = db.Column(db.DateTime, default=datetime.now())
    user = orm.relationship('User')
    chat = orm.relationship('Chat')


class Post(SqlAlchemyBase):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=True)
    user_login = db.Column(db.Integer, db.ForeignKey('users.login'))
    dt = db.Column(db.DateTime, default=datetime.now())
    user = orm.relationship('User')


class Chat(SqlAlchemyBase):
    __tablename__ = "chats"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    users = db.Column(db.String, nullable=False)
    message = orm.relationship('Message')