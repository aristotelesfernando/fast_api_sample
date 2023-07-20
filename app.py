# Importando os pacotes necessários
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db = "agenda.db"

# Criando o engine do SQLAlchemy com o recurso de URI
engine = create_engine(f"sqlite:///{db}?mode=rw", echo=True, connect_args={"uri": True})

# Criando a classe base para os modelos
Base = declarative_base()

# Criando a classe modelo para a tabela pessoas
class Pessoa(Base):
    __tablename__ = "pessoas"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String)
    data_nascimento = Column(String)
    phone = Column(String)

# Verificando se o banco de dados existe
if os.path.isfile(db):
    # Conectando ao banco de dados existente
    session = sessionmaker(bind=engine)()
else:
    # Criando um novo banco de dados e a tabela pessoas
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

# Criando um modelo Pydantic para validar os dados da API
class PessoaModel(BaseModel):
    nome: str
    email: str
    data_nascimento: str
    phone: str

# Criando uma instância do FastAPI
app = FastAPI()

# Criando uma rota para listar todas as pessoas da tabela
@app.get("/pessoas")
def listar_pessoas():
    pessoas = session.query(Pessoa).all()
    return pessoas

# Criando uma rota para criar uma nova pessoa na tabela
@app.post("/pessoas")
def criar_pessoa(pessoa: PessoaModel):
    nova_pessoa = Pessoa(
        nome=pessoa.nome,
        email=pessoa.email,
        data_nascimento=pessoa.data_nascimento,
        phone=pessoa.phone
    )
    session.add(nova_pessoa)
    session.commit()
    return nova_pessoa

# Criando uma rota para obter uma pessoa específica da tabela pelo id
@app.get("/pessoas/{id}")
def obter_pessoa(id: int):
    pessoa = session.query(Pessoa).get(id)
    if pessoa is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return pessoa

# Criando uma rota para atualizar uma pessoa específica da tabela pelo id
@app.put("/pessoas/{id}")
def atualizar_pessoa(id: int, pessoa: PessoaModel):
    pessoa_atualizada = session.query(Pessoa).get(id)
    if pessoa_atualizada is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    pessoa_atualizada.nome = pessoa.nome
    pessoa_atualizada.email = pessoa.email
    pessoa_atualizada.data_nascimento = pessoa.data_nascimento
    pessoa_atualizada.phone = pessoa.phone
    session.commit()
    return pessoa_atualizada

# Criando uma rota para deletar uma pessoa específica da tabela pelo id
@app.delete("/pessoas/{id}")
def deletar_pessoa(id: int):
    pessoa_deletada = session.query(Pessoa).get(id)
    if pessoa_deletada is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    session.delete(pessoa_deletada)
    session.commit()
    return {"message": "Pessoa deletada com sucesso"}
