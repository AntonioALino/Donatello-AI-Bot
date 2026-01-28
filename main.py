import nextcord as discord
import os
import httpx
from dotenv import load_dotenv
import re 
from unidecode import unidecode 
from typing import List


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID')) 

API_URL = "http://127.0.0.1:8000" 

intents = discord.Intents.default()
intents.members = True 

bot = discord.Client(intents=intents) 

TAGS_IGNORADAS = {
    'admin', 'mentor(a)', 'colaborador(a)', 'buscando mentoria', 
    'buscando vagas', 'divulgando', 'networking'
}

def normalizar_tags(role_names: List[str]) -> List[str]:

    tags_limpas = set()
    for role in role_names:
        role_lower = role.lower()
        if role_lower in TAGS_IGNORADAS:
            continue
        tag_sem_acento = unidecode(role_lower)
        partes = re.split(r'\s*/\s*', tag_sem_acento)
        for parte in partes:
            tag_final = re.sub(r'[^a-z0-9-]', '', parte)
            if tag_final:
                tags_limpas.add(tag_final)
    return list(tags_limpas)

@bot.event
async def on_ready():
    print(f'Pronto! Donatello AI está online como {bot.user} 🐢')


@bot.slash_command(name="vagas", 
                   description="Busca vagas com base nas suas tags (roles) do Discord.",
                   guild_ids=[GUILD_ID])
async def vagas(ctx: discord.Interaction): 
    
    await ctx.response.defer(ephemeral=True)

    member = ctx.user 
    
    role_names_sujos = [role.name for role in member.roles if role.name != "@everyone"]

    if not role_names_sujos:
        await ctx.followup.send(f'Olá, {member.display_name}. Você não possui nenhuma tag (cargo)...', ephemeral=True)
        return

    role_names_limpos = normalizar_tags(role_names_sujos)

    if not role_names_limpos:
        await ctx.followup.send(f'Olá, {member.display_name}. Suas tags de perfil ({", ".join(role_names_sujos)}) foram filtradas e não encontrei nenhuma tag de tecnologia (como Junior, Python, etc.) para buscar.', ephemeral=True)
        return

    tags_formatadas = ", ".join(role_names_limpos)
    print(f"Bot: Buscando vagas para {member.name} com as tags LIMPAS: {tags_formatadas}")

    async with httpx.AsyncClient() as client:
        try:
            params = {"tags": role_names_limpos}
            response = await client.get(f"{API_URL}/vagas", params=params)
            response.raise_for_status() 
            vagas_encontradas = response.json()
        except httpx.ConnectError:
            await ctx.followup.send(f"🐢 Opa! Não consegui conectar na API de vagas (`{API_URL}`). Ela está rodando?", ephemeral=True)
            return
        except httpx.HTTPStatusError as e: 
            await ctx.followup.send(f"🐢 A API de vagas retornou um erro: `{e.response.status_code}`. Verifique o log do `uvicorn`.", ephemeral=True)
            return
        except Exception as e:
            await ctx.followup.send(f"Ocorreu um erro inesperado: {e}", ephemeral=True)
            return

    if not vagas_encontradas:
        await ctx.followup.send(f"Nenhuma vaga encontrada no momento para as suas tags: **{tags_formatadas}**", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🐢 Vagas Encontradas para seu perfil",
        description=f"Baseado nas suas tags ({tags_formatadas}), encontrei {len(vagas_encontradas)} vagas. Aqui estão as 5 primeiras:",
        color=discord.Color.green()
    )

    for vaga in vagas_encontradas[:5]:
        embed.add_field(
            name=f"💼 {vaga['titulo']}",
            value=(
                f"**Empresa:** {vaga['empresa']}\n"
                f"**Tags da Vaga:** {', '.join(vaga['tags'])}\n"
                f"**[Ver Vaga]({vaga['link']})**"
            ),
            inline=False
        )
    
    embed.set_footer(text="Donatello AI - By Donatello AI")
    
    await ctx.followup.send(embed=embed, ephemeral=True)

@bot.slash_command(name="analisar_vaga_custom", 
                   description="Analisa uma vaga que você colar aqui contra o seu currículo.",
                   guild_ids=[GUILD_ID])
async def analisar_vaga_custom(ctx: discord.Interaction):
    await ctx.response.send_message("Em breve você poderá analisar vagas aqui...", ephemeral=True)

if TOKEN:
    bot.run(TOKEN)
else:
    print("Erro: DISCORD_TOKEN não encontrado. Verifique seu arquivo .env")