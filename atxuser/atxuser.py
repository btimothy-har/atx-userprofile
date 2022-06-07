from redbot.core import Config, commands, bank
from numerize import numerize
from discord.utils import get
from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice
from tabulate import tabulate
from datetime import datetime
import time
import asyncio
import discord
import requests
import json
import datetime
import pytz
import random

from mee6rank.mee6rank import Mee6Rank

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
            "name": "",
            "age": 0,
            "location": "",
            "statement": "",
            "codm": [],
            "apexmobile": []
        }       
        self.config.register_global(**defaults_global)
        self.config.register_user(**defaults_user)

    @commands.command(name="profileset")
    async def profilesettings(self,ctx):
        """Set up your User Profile."""

        complete = False

        skipText = "\n\u200b\nTo skip this question, simply type `skip`."

        currName = await self.config.user(ctx.author).name()
        currAge = await self.config.user(ctx.author).age()

        await ctx.send(f"{ctx.author.mention} I will DM you to continue the set up process. Please ensure your DMs are open!")
        await ctx.author.send("Hello! Let's set up your profile in Ataraxy. I'll be asking you a few questions. Feel free to answer in any way you like - your profile is customizable as you like it :-). You'll have an opportunity to confirm all your entries before saving.\n\nSend any message to get started.")

        try:
            startmsg = await ctx.bot.wait_for("message", timeout=60)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")

        def str_check(m):
            return m.author == ctx.author and m.guild is None and len(m.content) <= 600

        def age_check(m):
            return m.author == ctx.author and m.guild is None and ((m.content.isdigit() and int(m.content) >= 0) or m.content == "skip")

        def confirm_check(m):
            return m.author == ctx.author and m.guild is None and (m.content.lower() == "yes" or m.content.lower() == "no")

        await ctx.author.send(f"`What should people call you?`{skipText}")
        try:
            name = await ctx.bot.wait_for("message", timeout=60, check=str_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        if name.content == 'skip':
            name = ""
        else:
            name = name.content

        await ctx.author.send(f"`How old are you?`\nPlease enter a number.{skipText}")
        try:
            age = await ctx.bot.wait_for("message", timeout=60, check=age_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        if age.content == 'skip':
            age = 0
        else:
            age = int(age.content)

        await ctx.author.send(f"`Where are you from?`{skipText}")
        try:
            location = await ctx.bot.wait_for("message", timeout=60, check=str_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        if location.content == 'skip':
            location = ""
        else:
            location = location.content

        await ctx.author.send(f"`Type a personal statement to be shown on your profile.`\nMaximum of 600 characters.{skipText}")
        try:
            statement = await ctx.bot.wait_for("message", timeout=120, check=str_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        if statement.content == 'skip':
            statement = ""
        else:
            statement = statement.content

        embed = await profile_embed(ctx=ctx,
                    message=f"Please confirm your entries below. You will need to start over if any are incorrect.\n\nRespond with `yes` or `no` to confirm.",
                    show_author=True)
        embed.add_field(
            name=f"Name/Nickname",
            value=f"{name}",
            inline=False)
        embed.add_field(
            name=f"Age",
            value=f"{age}",
            inline=False)
        embed.add_field(
            name=f"Location",
            value=f"{location}",
            inline=False)
        embed.add_field(
            name=f"Personal Statement",
            value=f"{statement}",
            inline=False)
        await ctx.author.send(embed=embed)

        try:
            confirm = await ctx.bot.wait_for("message", timeout=60, check=confirm_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")

        if confirm.content.lower() == "yes":
            await self.config.user(ctx.author).name.set(name)
            await self.config.user(ctx.author).age.set(age)
            await self.config.user(ctx.author).location.set(location)
            await self.config.user(ctx.author).statement.set(statement)
            return await ctx.author.send("Your profile is all set up! You can view it from the Ataraxy server.")
        else:
            return await ctx.author.send("Cancelled. Your profile was not modified.")    

    @commands.command(name="whois")
    async def user_info(self, ctx: commands.Context, user: discord.Member = None):
        """Show your profile, or that of another user."""
        
        if user is None:
            user = ctx.author

        if user.bot:
            return

        if user.activity:
            activity_desc = f" - {user.activity}"
        else:
            activity_desc = ""

        if user.premium_since:
            booster_timediff = datetime.datetime.now() - user.premium_since
            booster_desc = f"\n**Boosting since {booster_timediff.days} day(s) ago.**"
        else:
            booster_desc = ""

        userStatementSet = await self.config.user(user).statement()
        if userStatementSet == "":
            userStatement = "\n\u200b\n*You can include a personal message here for Ataraxy. Set up your profile with `;profileset`.*"
        else:
            userStatement = f"\n\u200b\n*{userStatementSet}*"

        embed = await profile_embed(ctx=ctx,
                    title=f"{user.name}#{user.discriminator}",
                    message=f"{user.mention}{activity_desc}{booster_desc}{userStatement}\n\u200b",
                    show_author=False)

        embed.set_thumbnail(url=user.avatar_url)

        joined_timediff = datetime.datetime.now() - user.joined_at
        registered_timediff = datetime.datetime.now() - user.created_at

        embed.add_field(
            name=f"**Joined {user.guild}**",
            value=f"{user.joined_at.strftime('%b %d, %Y')}\n{joined_timediff.days} day(s) ago",
            inline=True)

        embed.add_field(
            name=f"**First seen on Discord**",
            value=f"{user.created_at.strftime('%b %d, %Y')}\n{registered_timediff.days} day(s) ago",
            inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="mr")
    async def mee6test(self, ctx: commands.Context):
        """Show your profile, or that of another user."""
        i = Mee6Rank._maybe_get_player(ctx.author)

        await ctx.send(i.level)