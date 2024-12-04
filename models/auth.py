import sqlalchemy

from pydantic import BaseModel

from db import Users, connectDB

class Auth(BaseModel):
    login: str
    password: str


def checkAuthUser(session: str) -> bool:
    '''
    Проверяет существует ли сессия
    '''
    genSql = sqlalchemy.select(Users).where(
        Users.jwt == session
    )
    data = connectDB.execute(genSql).fetchone()

    if data:
        return True
    return False