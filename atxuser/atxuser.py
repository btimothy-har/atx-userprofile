from redbot.core import Config, commands, bank
from numerize import numerize
from discord.utils import get
from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice
from tabulate import tabulate
import time
import asyncio
import discord
import requests
import json
import datetime
import pytz
import random

async def profile_embed(ctx, title=None, message=None, url=None, show_author=True, color=None):
    if not title:
        title = ""
    if not message:
        message = ""
    if color == "success":
        color = 0x00FF00
    elif color == "fail":
        color = 0xFF0000
    else:
        color = await ctx.embed_color()
    if url:
        embed = discord.Embed(title=title,url=url,description=message,color=color)
    else:
        embed = discord.Embed(title=title,description=message,color=color)
    if show_author:
        embed.set_author(name=f"{ctx.author.display_name}#{ctx.author.discriminator}",icon_url=ctx.author.avatar_url)    
    embed.set_footer(text="The Ataraxy Community",icon_url="https://i.imgur.com/xXjjWke.png")
    return embed


class AtaraxyProfile(commands.Cog):
    """Manage your Ataraxy Member profile below."""
    def __init__(self):
        self.config = Config.get_conf(self, identifier=828462461169696778,force_registration=True)
        defaults_global = {}
        defaults_user = {
            "age": 0,
            "location": "",
            "codm": [
                {
                "server": "",
                "ign": ""
                }
            ]
            "apexmobile": [
                {
                "ign": ""
                }
            ]
        }       
        self.config.register_global(**defaults_global)
        self.config.register_user(**defaults_user)

    @commands.group(name="profileset")
    async def profilesettings(self,ctx):
        """Group commands to manage your User Profile."""
    

    @commands.command(name="whois", aliases=['myprofile'])
    async def user_info(self, ctx: commands.Context, user: discord.Member = None):
        """Show your profile, or that of another user."""
        
        if user is None:
            user = ctx.author

        if user.bot:
            return

        embed = await profile_embed(ctx=ctx,
                    title=f"{user.name}#{user.discriminator}",
                    message=f"{user.mention}")

        embed.add_field(
            name=f"**Joined {user.guild}**",
            value=f"{user.joined_at}",
            inline=True)

        embed.add_field(
            name=f"**First seen on Discord**",
            value=f"{user.created_at}",
            inline=True)
        
        await ctx.send(embed=embed)