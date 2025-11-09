import asyncio
from tortoise import Tortoise, run_async
from scraper import buscar_vagas 
from models import Vaga
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

URLS_PARA_RASPAR = [
    {"url": "https://programathor.com.br/jobs", "tag_extra": "remoto"},
    {"url": "https://programathor.com.br/jobs-city/sorocaba", "tag_extra": "sorocaba"},
]

async def init_db():
    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["models"]})
    await Tortoise.generate_schemas()

async def salvar_vagas_no_banco():
    await init_db()
    print("Iniciando o scraper (Playwright Manual) para popular o banco...")
    vagas_novas_total = 0
    
    for alvo in URLS_PARA_RASPAR:
        vagas_coletadas = await buscar_vagas(alvo["url"], alvo["tag_extra"])
        
        if not vagas_coletadas:
            print(f"Nenhuma vaga encontrada em '{alvo['url']}'.")
            continue

        print(f"{len(vagas_coletadas)} vagas encontradas em '{alvo['url']}'. Salvando...")
        vagas_novas_neste_alvo = 0
        
        for vaga_data in vagas_coletadas:
            vaga, created = await Vaga.get_or_create(link=vaga_data['link'], defaults=vaga_data)
            if created: vagas_novas_neste_alvo += 1
            
        print(f"{vagas_novas_neste_alvo} novas vagas salvas deste alvo.")
        vagas_novas_total += vagas_novas_neste_alvo

    await Tortoise.close_connections()
    print(f"Processo concluído. {vagas_novas_total} novas vagas foram salvas no total.")

if __name__ == "__main__":
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não foi encontrada no .env.")
    run_async(salvar_vagas_no_banco())