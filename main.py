import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Charger le .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="&", intents=intents, help_command=None)

BLACKLIST_FILE = "blacklist.json"

# Charger la blacklist depuis un fichier JSON
def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

# Sauvegarder la blacklist dans un fichier JSON
def save_blacklist():
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(list(blacklist), f)

blacklist = load_blacklist()

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

@bot.event
async def on_member_join(member):
    if member.id in blacklist:
        try:
            await member.ban(reason="Blacklist globale")
            print(f"🚫 {member} a été banni car il est sur la blacklist.")
        except Exception as e:
            print(f"Erreur ban {member}: {e}")

# ===================== BLACKLIST =====================
@bot.group()
async def bl(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("⚠️ Utilise : `&bl add <id>`, `&bl remove <id>`, ou `&bl list`")

@bl.command()
async def add(ctx, user_id: int):
    blacklist.add(user_id)
    save_blacklist()
    await ctx.send(f"✅ L'utilisateur `{user_id}` a été ajouté à la blacklist.")

@bl.command()
async def remove(ctx, user_id: int):
    if user_id in blacklist:
        blacklist.remove(user_id)
        save_blacklist()
        await ctx.send(f"✅ L'utilisateur `{user_id}` a été retiré de la blacklist.")
    else:
        await ctx.send("❌ Cet utilisateur n'était pas blacklisté.")

@bl.command(name="list")
async def _list(ctx):
    if not blacklist:
        await ctx.send("📭 La blacklist est vide.")
    else:
        ids = "\n".join(str(uid) for uid in blacklist)
        await ctx.send(f"🚫 Utilisateurs blacklistés :\n```{ids}```")

# ===================== HELP =====================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📖 Aide du bot",
        description="Voici la liste des commandes disponibles :",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="⚙️ Blacklist",
        value=(
            "`&bl add <id>` → Ajouter un utilisateur à la blacklist\n"
            "`&bl remove <id>` → Retirer un utilisateur de la blacklist\n"
            "`&bl list` → Voir la liste des utilisateurs blacklistés"
        ),
        inline=False
    )

    embed.add_field(
        name="ℹ️ Général",
        value="`&help` → Affiche ce message d’aide",
        inline=False
    )

    await ctx.send(embed=embed)

# ===================== RUN =====================
bot.run(TOKEN)
