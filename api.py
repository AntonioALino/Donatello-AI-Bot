from fastapi import FastAPI, Query 
from tortoise import Tortoise
from models import Vaga
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import Optional, List
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL não foi encontrada no .env. Verifique seu arquivo .env")

Vaga_Pydantic = pydantic_model_creator(Vaga, name="Vaga")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("API iniciando... Conectando ao banco de dados Postgres...")
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()
    print("Conexão estabelecida e schemas gerados.")
    yield
    print("API desligando... Fechando conexões com o banco.")
    await Tortoise.close_connections()

app = FastAPI(
    title="Donatello AI - Agregador de Vagas",
    version="1.2.0", 
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Donatello AI API (Postgres) está online! 🐢"}

@app.get("/vagas", response_model=List[Vaga_Pydantic])
async def get_vagas(
    tags: Optional[List[str]] = Query(None) 
):
 
    print(f"API: Endpoint /vagas chamado. Filtro de tags: {tags}")
    
    if not tags:
        return await Vaga.all() 

    tags_normalizadas = [tag.lower() for tag in tags]
    
    
    query = Vaga.filter(tags__overlap=tags_normalizadas)
    
    tem_junior = 'junior' in tags_normalizadas
    tem_pleno = 'pleno' in tags_normalizadas
    tem_senior = 'senior' in tags_normalizadas

    if (tem_junior or tem_pleno) and not tem_senior:
        print("Filtro: Usuário é Junior/Pleno, não Senior. Excluindo vagas 'senior'.")
     
        query = query.exclude(tags__contains=['senior'])
        
    if tem_senior and not (tem_junior or tem_pleno):
        print("Filtro: Usuário é Senior, não Junior/Pleno. Excluindo vagas 'junior' e 'pleno'.")
        query = query.exclude(tags__contains=['junior']).exclude(tags__contains=['pleno'])
        
    
    return await query.all()