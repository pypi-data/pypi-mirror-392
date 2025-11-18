from .identify import identify
from discord.gateway import DiscordWebSocket
from .main import api

__all__ = ["api"]
__version__ = "0.1.5"
DiscordWebSocket.identify = identify