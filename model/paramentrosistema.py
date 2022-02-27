from sqlalchemy import Column, Integer, String

from controller.sqlalchemy_start import sqlalchemy_starter

Session, Base, engine = sqlalchemy_starter()


class ParametroSistema(Base):
    __tablename__ = 'parametrosistema'
    id = Column(Integer, primary_key=True)
    nome = Column('nome', String)
    valor = Column('valor', String)

    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor
