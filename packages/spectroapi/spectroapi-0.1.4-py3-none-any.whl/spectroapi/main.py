from __future__ import annotations
import os
from typing import Optional
import aiohttp
import discord
from discord.ext import commands
BASE_URL = os.getenv("SPECTROAPI_BASE_URL", "https://xvz.wtf").rstrip("/")
class SpectroAPIClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base = BASE_URL
    async def get_categories(self) -> list[str]:
        async with self.session.get(f"{self.base}/categories") as resp:
            if resp.status != 200:
                raise RuntimeError(f"Categories endpoint returned {resp.status}")
            data = await resp.json()
            return data["categories"]
    async def get_random_image(
        self,
        *,
        category: Optional[str] = None,
        force_random: bool = True,
    ) -> dict[str, str]:
        params = {}
        if category:
            params["category"] = category
        if force_random:
            params["random"] = "true"

        async with self.session.get(self.base, params=params) as resp:
            if resp.status == 404:
                data = await resp.json()
                raise ValueError(data.get("message", "No images"))
            if resp.status != 200:
                raise RuntimeError(f"Image endpoint returned {resp.status}")
            return await resp.json()
class SpectroAPI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.http = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        self.categories: list[str] = ["anime", "egirl"]  # fallback
        self.bot.loop.create_task(self._load_categories())

    async def _load_categories(self) -> None:
        client = SpectroAPIClient(self.http)
        try:
            self.categories = await client.get_categories()
        except Exception:
            pass
    async def cog_unload(self) -> None:
        await self.http.close()
    @commands.command(name="pfps", aliases=["p"])
    async def pfps(self, ctx: commands.Context, category: Optional[str] = None) -> None:
        client = SpectroAPIClient(self.http)
        cat = None if category and category.lower() == "all" else category
        try:
            data = await client.get_random_image(category=cat)
        except ValueError as e:
            await ctx.send(f"Error: {e}")
            return
        except Exception:
            await ctx.send("Error: API error.")
            return
        embed = discord.Embed(title="Random PFP", colour=discord.Colour.blurple())
        embed.set_image(url=data["link"])
        embed.set_footer(text=f"Category: {data['category']}")

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Open Original",
                style=discord.ButtonStyle.link,
                url=data["link"],))
        await ctx.send(embed=embed, view=view)
    async def _autocomplete_category(self, interaction: discord.Interaction, current: str):
        choices = [
            discord.app_commands.Choice(name=c.title(), value=c)
            for c in self.categories
            if current.lower() in c.lower()]
        await interaction.response.send_autocomplete(choices[:25])
    @pfps.autocomplete("category")
    async def category_autocomplete(self, interaction: discord.Interaction, current: str):
        await self._autocomplete_category(interaction, current)
api = SpectroAPI