import jwt, sqlalchemy, logging

from db import connectDB, Users

from fastapi import FastAPI

from models.auth import Auth, checkAuthUser
from models.translate import Translate


app = FastAPI()
logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w")

@app.post("/registr")
async def _(auth: Auth):

    if (auth.login is None or auth.password is None):
        logging.error("Попытка отправки пустой формы")
        return {"error": "введите логин и парль"}
    
    genSql = sqlalchemy.select(Users).where(
        Users.login == auth.login
    )
    res = connectDB.execute(genSql).fetchall()
    
    if res != []:
        logging.error("Попытка регистрации с неверным логином/паролем data: login: {} \n password: {}".format(auth.login, auth.password))
        return {"error": "Логин занят, выберите другой."}
    
    genSql = sqlalchemy.insert(Users).values(
        {
            Users.login: auth.login,
            Users.password: auth.password
        }
    )
    connectDB.execute(genSql)
    connectDB.commit()
    logging.info("Пользователь {} зарегистрирован".format(auth.login))
    return {"message": "success"}



@app.post("/auth")
async def _(auth: Auth):

    if (auth.login is None or auth.password is None):
        logging.error("Попытка отправки пустой формы")
        return {"error": "введите логин и парль"}
    
    genSql = sqlalchemy.select(Users).where(
        Users.login == auth.login,
        Users.password == auth.password
    )
    res = connectDB.execute(genSql).fetchone()

    if res is None:
        logging.error("Попытка входа с неверным логином/паролем data: login: {} \n password: {}".format(auth.login, auth.password))
        return {"error": "Неверный логин/пароль"}
    
    resJwt = jwt.encode(
        {"login": auth.login},
        "secret",
        algorithm="HS256"
    )

    genSql = sqlalchemy.insert(Users).values(
        {
            Users.jwt: resJwt
        }
    )
    connectDB.execute(genSql)
    connectDB.commit()
    
    logging.info("Пользователь {} выполнил вход".format(auth.login))

    return {
        "message": "success",
        "session": resJwt
    }



@app.get("/info_user")
async def _(session: str):
    
    info = jwt.decode(session, "secret", algorithms=["HS256"])

    genSql = sqlalchemy.select(Users).where(
        Users.login == info['login']
    )
    data = connectDB.execute(genSql).fetchone()

    return {
        "id": data[0],
        "login": str(data[1]),
        "cash": data[4] or 0
    }



@app.post("/translate")
async def _(translate: Translate):

    if checkAuthUser(translate.session):

        genSql = sqlalchemy.select(Users).where(
            Users.jwt == translate.session
        )
        dataCurUser = connectDB.execute(genSql).fetchone()

        genSql = sqlalchemy.select(Users).where(
            Users.id == translate.user_id
        )
        dataArrderssUser = connectDB.execute(genSql).fetchone()

        if float(dataCurUser[4]) < float(translate.summ):
            logging.error("Пользователь {} пытался перевести больше средств чем имеет".format(dataCurUser[1]))
            return {
                'error': 'Недостаточно средств'
            }
        
        newBalanseCurrUser = connectDB.execute(
            sqlalchemy.text("UPDATE users SET cash = cash - {} WHERE id = {} RETURNING cash;".format(
                translate.summ,
                dataCurUser[0]
                ))
        ).fetchone()

        newBalanseAddressUser = connectDB.execute(
            sqlalchemy.text("UPDATE users SET cash = cash + {} WHERE id = {} RETURNING cash;".format(
                translate.summ,
                dataArrderssUser[0]
                ))
        ).fetchone()
        
        
        oldSumm = dataCurUser[4] + dataArrderssUser[4]
        newSumm = newBalanseCurrUser[0] + newBalanseAddressUser[0]

        if oldSumm >= newSumm:
            connectDB.commit()

            logging.info("Пользователь {} перевел пользователю {} сумму: {}".format(dataCurUser[1], dataArrderssUser[1], translate.summ))

            return {
                'message': 'success'
            }
        return {
            'message': 'error'
        }