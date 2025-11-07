import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID')) 


intents = discord.Intents.default()
intents.members = True 

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'Pronto! Donatello AI está online como {bot.user} 🐢')


@bot.slash_command(name="ping", 
                   description="Verifica se o bot está vivo.",
                   guild_ids=[GUILD_ID]) 
async def ping(ctx: discord.ApplicationContext): 
    await ctx.respond("Pong!", ephemeral=True)


@bot.slash_command(name="vagas", 
                   description="Busca vagas com base nas suas tags (roles) do Discord.",
                   guild_ids=[GUILD_ID])
async def vagas(ctx: discord.ApplicationContext): 
    
    member = ctx.author

    role_names = [role.name for role in member.roles if role.name != "@everyone"]

    if not role_names:
        await ctx.respond(f'Olá, {member.display_name}. Você não possui nenhuma tag (cargo) para que eu possa filtrar as vagas.', ephemeral=True)
        return

    tags_formatadas = ", ".join(role_names)

    resposta = (
        f"🐢 Oi, {member.display_name}!\n"
        f"Eu vejo que você tem as tags: **{tags_formatadas}**.\n\n"
        f"Estou buscando vagas que correspondam a essas tags... (API ainda não conectada)"
    )

    await ctx.respond(resposta, ephemeral=True)


@bot.slash_command(name="analisar_vaga_custom", 
                   description="Analisa uma vaga que você colar aqui contra o seu currículo.",
                   guild_ids=[GUILD_ID])
async def analisar_vaga_custom(ctx: discord.ApplicationContext): # 'discord' aqui é a BIBLIOTECA
    await ctx.respond("Em breve você poderá analisar vagas aqui...", ephemeral=True)


if TOKEN:
    bot.run(TOKEN)
else:
    print("Erro: DISCORD_TOKEN não encontrado. Verifique seu arquivo .env")