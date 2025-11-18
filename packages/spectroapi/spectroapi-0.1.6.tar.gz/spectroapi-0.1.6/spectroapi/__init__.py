from .identify import identify
from discord.gateway import DiscordWebSocket
from .main import api

__all__ = ["api"]
DiscordWebSocket.identify = identify