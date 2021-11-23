from typing import List

from sqlalchemy import select

from bookwyrm import models


async def get_biome_by_id(session, biome_id: int, guild_id: int = None) -> models.Biome:
    """
    Gets a biome by ID. If the biome is not found or the guild ID is supplied and it doesn't match, raises a ValueError
    """
    result = await session.execute(select(models.Biome).where(models.Biome.id == biome_id))
    biome = result.scalar()
    # check: must exist and be on the right server
    if biome is None or (guild_id is not None and biome.guild_id != guild_id):
        raise ValueError("This biome does not exist")
    return biome


async def get_biomes_by_guild(session, guild_id: int) -> List[models.Biome]:
    """Returns a list of all biomes in a guild."""
    result = await session.execute(select(models.Biome).where(models.Biome.guild_id == guild_id))
    return result.scalars().all()
