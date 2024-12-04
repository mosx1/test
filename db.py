from sqlalchemy import create_engine, Column, Text, BigInteger, PrimaryKeyConstraint, UniqueConstraint, Numeric
from sqlalchemy.ext.declarative import declarative_base

db = create_engine('')
connectDB =  db.connect()

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(BigInteger)
    login = Column(Text(), nullable=True)
    password = Column(Text(), nullable=True)
    jwt = Column(Text())
    cash = Column(Numeric())

    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pk'),
        UniqueConstraint('login')
    )

#Base.metadata.create_all(db)