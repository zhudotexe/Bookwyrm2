from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class Biome(Base):
    __tablename__ = "biomes"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    name = Column(String, nullable=False)
    city_id = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)

    channels = relationship("ChannelMap", back_populates="biome")

    def __repr__(self):
        return (f"<{type(self).__name__} id={self.id!r} guild_id={self.guild_id!r} name={self.name!r} "
                f"city_id={self.city_id!r} image_url={self.image_url!r}>")


class ChannelMap(Base):
    __tablename__ = "channel_map"

    channel_id = Column(BigInteger, primary_key=True)
    biome_id = Column(Integer, ForeignKey("biomes.id", ondelete="CASCADE"))

    biome = relationship("Biome", back_populates="channels")

    def __repr__(self):
        return f"<{type(self).__name__} id={self.id!r} biome_id={self.biome_id!r}>"
