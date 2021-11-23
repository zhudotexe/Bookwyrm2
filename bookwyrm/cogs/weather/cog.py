from typing import Any

import disnake
from disnake.ext import commands
from sqlalchemy import delete

from bookwyrm import db, models
from . import utils
from .params import biome_param, city_param
from .city import CityRepository


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_slash_command_check(self, inter: disnake.ApplicationCommandInteraction) -> bool:
        """All weather commands must be run in a guild"""
        if inter.guild_id is None:
            raise commands.CheckFailure("This command can only be run in a server")
        return True

    # ==== public ====
    @commands.slash_command(description="Shows the weather")
    async def weather(
        self,
        inter: disnake.ApplicationCommandInteraction,
        biome: Any = biome_param(None, desc="The ID of the biome to get the weather of")
    ):
        pass
        # hTTP https://api.openweathermap.org/data/2.5/weather?id=12345&appid=0f2223471182591c54d4721271e15f99

    # ==== admin ====
    @commands.slash_command(name='weatheradmin', description="Create/remove biomes and channel links")
    async def weatheradmin(self, inter: disnake.ApplicationCommandInteraction):
        # role-locked to Dragonspeaker
        if not any(r.name == 'Dragonspeaker' for r in inter.author.roles):
            raise commands.CheckFailure("Only Dragonspeakers can run this command")

    # ---- channel ----
    @weatheradmin.sub_command_group(name='channel')
    async def weatheradmin_channel(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @weatheradmin_channel.sub_command(name='link', description="Link a channel to a biome")
    async def weatheradmin_channel_link(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @weatheradmin_channel.sub_command(name='unlink', description="Unlink a channel from a biome")
    async def weatheradmin_channel_unlink(self, inter: disnake.ApplicationCommandInteraction):
        pass

    # ---- biome ----
    @weatheradmin.sub_command_group(name='biome')
    async def weatheradmin_biome(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @weatheradmin_biome.sub_command(name='list', description="Lists the biomes and their IDs")
    async def weatheradmin_biome_list(self, inter: disnake.ApplicationCommandInteraction):
        async with db.async_session() as session:
            biomes = await utils.get_biomes_by_guild(session, inter.guild_id)
        if not biomes:
            await inter.send("This server has no biomes. Make some with `/weatheradmin biome create`.")
            return
        out = []
        for biome in biomes:
            biome_city = CityRepository.get_city(biome.city_id)
            out.append(f'`{biome.id}` - **{biome.name}** (Weather from {biome_city.name}, {biome_city.state})')
        await inter.send('\n'.join(out))

    @weatheradmin_biome.sub_command(name='create', description="Create a new biome")
    async def weatheradmin_biome_create(
        self,
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(desc="The name of the biome"),
        city: Any = city_param(desc="The IRL city the biome uses for weather"),
        image_url: str = commands.Param(None, desc="The image to show in /weather")
    ):
        new_biome = models.Biome(name=name, guild_id=inter.guild_id, city_id=city.id, image_url=image_url)
        async with db.async_session() as session:
            session.add(new_biome)
            await session.commit()
        await inter.send(
            f"Created the biome `{new_biome.name}` (ID {new_biome.id}). "
            f"Now link it to some channels with `/weatheradmin channel link`!"
        )

    @weatheradmin_biome.sub_command(name='edit', description="Edit a biome")
    async def weatheradmin_biome_edit(
        self,
        inter: disnake.ApplicationCommandInteraction,
        biome: Any = biome_param(desc="The ID of the biome to edit"),
        name: str = commands.Param(None, desc="The name of the biome"),
        city: Any = city_param(None, desc="The IRL city the biome uses for weather"),
        image_url: str = commands.Param(None, desc="The image to show in /weather")
    ):
        async with db.async_session() as session:
            session.add(biome)

            # update attrs
            if name is not None:
                biome.name = name
            if city is not None:
                biome.city_id = city.id
            if image_url is not None:
                biome.image_url = image_url

            await session.commit()
        await inter.send(f"Updated the biome `{biome.name}` (ID {biome.id}).")

    @weatheradmin_biome.sub_command(name='delete', description="Delete a biome")
    async def weatheradmin_biome_delete(
        self,
        inter: disnake.ApplicationCommandInteraction,
        biome: Any = biome_param(desc="The ID of the biome to delete")
    ):
        async with db.async_session() as session:
            await session.execute(delete(models.Biome).where(models.Biome.id == biome.id))
            await session.commit()

        await inter.send(f"Deleted the biome `{biome.name}` (ID {biome.id}).")