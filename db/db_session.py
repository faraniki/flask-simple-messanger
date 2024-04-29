import sqlalchemy as dba
from sqlalchemy import orm


SqlAlchemyBase = orm.declarative_base()
__factory = None


def init(file):
    global __factory
    global SqlAlchemyBase

    if __factory:
        return

    conn_str = f"sqlite:///{file.strip(' ')}"

    engine = dba.create_engine(conn_str)

    __factory = orm.sessionmaker(bind=engine)

    from db.__all_models import User, Message

    SqlAlchemyBase.metadata.create_all(bind=engine)


def create_sesion() -> orm.Session:
    global __factory
    return __factory()