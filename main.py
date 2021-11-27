import logging

import disnake
from disnake.ext import commands

from bookwyrm import config, db

COGS = ('bookwyrm.cogs.weather',)

logging.basicConfig(level=logging.INFO)


class Bookwyrm(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


intents = disnake.Intents.all()
bot = Bookwyrm(
    command_prefix=commands.when_mentioned,
    intents=intents,
    sync_commands_debug=True,
    test_guilds=[
        810637213171449876,  # server.exe
        862504698341490709,  # tyre
        912886971934863380,  # weather beep boop
    ],
)


# === listeners ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.event
async def on_slash_command_error(inter, error):
    await inter.send(f"Error: {error!s}", ephemeral=True)


# === commands ===
@bot.command()
async def ping(ctx):
    await ctx.send("Pong.")


for cog in COGS:
    bot.load_extension(cog)

if __name__ == '__main__':
    bot.loop.create_task(db.init_db())
    bot.run(config.TOKEN)
