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
from atxcoc.atxcoc import th_emotes
from atxcoc.coc_resources import Member

skipText = "\n\u200b\nTo skip this question, simply type `skip`."

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

    @commands.group(name="myinfo")
    async def profilesettings(self,ctx):
        """Admin settings """

    @profilesettings.command(name="setup")
    async def setup_profile(self,ctx):
        """Set up your User Profile."""
        currName = await self.config.user(ctx.author).name()
        currAge = await self.config.user(ctx.author).age()

        def dm_check(m):
            return m.author == ctx.author and m.guild is None

        await ctx.send(f"{ctx.author.mention} I will DM you to continue the set up process. Please ensure your DMs are open!")
        await ctx.author.send("Hello! Let's set up your profile in Ataraxy. I'll be asking you a few questions. Feel free to answer in any way you like - your profile is customizable as you like it :-). You'll have an opportunity to confirm all your entries before saving.\n\nSend any message to get started.")

        try:
            startmsg = await ctx.bot.wait_for("message", timeout=60, check=dm_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        
        def str_check(m):
            return m.author == ctx.author and m.guild is None and len(m.content) <= 600
        def age_check(m):
            return m.author == ctx.author and m.guild is None and ((m.content.isdigit() and int(m.content) >= 0) or m.content.lower() == "skip")
        def confirm_check(m):
            return m.author == ctx.author and m.guild is None and (m.content.lower() == "yes" or m.content.lower() == "no")

        await ctx.author.send(f"```What should people call you?```{skipText}")
        try:
            name = await ctx.bot.wait_for("message", timeout=60, check=str_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        if name.content.lower() == 'skip':
            name = ""
        else:
            name = name.content

        await ctx.author.send(f"```How old are you?```Please enter a number.{skipText}")
        try:
            age = await ctx.bot.wait_for("message", timeout=60, check=age_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        if age.content.lower() == 'skip':
            age = 0
        else:
            age = int(age.content)

        await ctx.author.send(f"```Where are you from?```{skipText}")
        try:
            location = await ctx.bot.wait_for("message", timeout=60, check=str_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        if location.content.lower() == 'skip':
            location = ""
        else:
            location = location.content

        await ctx.author.send(f"```Type a personal statement to be shown on your profile.```Maximum of 600 characters.{skipText}")
        try:
            statement = await ctx.bot.wait_for("message", timeout=120, check=str_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        if statement.content.lower() == 'skip':
            statement = ""
        else:
            statement = statement.content

        embed = await profile_embed(ctx=ctx,
                    message=f"**Please confirm your entries below. You will need to start over if any are incorrect.**\n\nRespond with `yes` or `no` to confirm.",
                    show_author=True)
        embed.add_field(
            name=f"Name/Nickname",
            value=f"{name}\u200b",
            inline=False)
        embed.add_field(
            name=f"Age",
            value=f"{age}\u200b",
            inline=False)
        embed.add_field(
            name=f"Location",
            value=f"{location}\u200b",
            inline=False)
        embed.add_field(
            name=f"Personal Statement",
            value=f"{statement}\u200b",
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

    @profilesettings.command(name="codm")
    async def setup_codm(self,ctx):
        """Set up your CODM Profile."""
        currCODM = await self.config.user(ctx.author).codm()

        await ctx.send(f"{ctx.author.mention} I will DM you to continue the set up process. Please ensure your DMs are open!")
        await ctx.author.send("Hello! Let's set up your Call Of Duty: Mobile profile in Ataraxy.\n\nSend any message to get started.")

        def dm_check(m):
            return m.author == ctx.author and m.guild is None

        try:
            startmsg = await ctx.bot.wait_for("message", timeout=60, check=dm_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")

        def server_check(m):
            return m.author == ctx.author and m.guild is None and (str(m.content.lower())=='garena' or str(m.content.lower())=='global')
        def gamemode_check(m):
            return m.author == ctx.author and m.guild is None and (str(m.content.lower())=='mp' or str(m.content.lower())=='br' or str(m.content.lower())=='both' or str(m.content.lower())=='skip')
        def confirm_check(m):
            return m.author == ctx.author and m.guild is None and (m.content.lower() == "yes" or m.content.lower() == "no")

        await ctx.author.send(f"```Which CODM Server do you play in?```Acceptable values: `Global` or `Garena`.")
        try:
            server = await ctx.bot.wait_for("message", timeout=30, check=server_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        server = server.content.lower()

        await ctx.author.send(f"```What's your in-game name (IGN)? Please do not put your User ID.```")
        try:
            ign = await ctx.bot.wait_for("message", timeout=60)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        ign = ign.content

        #await ctx.author.send(f"```Do you prefer playing MP, BR, or both?```Acceptable values: `MP`, `BR`, or `Both`.{skipText}")
        #try:
        #    gamemode = await ctx.bot.wait_for("message", timeout=60)
        #except asyncio.TimeoutError:
        #    return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        #if gamemode.content == 'skip':
        #    gamemode = ""
        #else:
        #    gamemode = gamemode.content

        embed = await profile_embed(ctx=ctx,
                    message=f"**Please confirm your entries below. You will need to start over if any are incorrect.**\n\nRespond with `yes` or `no` to confirm.",
                    show_author=True)
        embed.add_field(
            name=f"Server",
            value=f"{server.capitalize()}",
            inline=False)
        embed.add_field(
            name=f"In-Game Name (IGN)",
            value=f"{ign}",
            inline=False)
        #embed.add_field(
        #    name=f"Game Mode",
        #    value=f"{gamemode.upper()}\u200b",
        #    inline=False)
        await ctx.author.send(embed=embed)

        try:
            confirm = await ctx.bot.wait_for("message", timeout=60, check=confirm_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")

        if confirm.content.lower() == "yes":
            codmData = [
                {
                    "server": server.capitalize(),
                    "ign": ign,
                    "gamemode": "",
                    }
                ]
            await self.config.user(ctx.author).codm.set(codmData)
            return await ctx.author.send("Your CODM is now set up! You can view it from the Ataraxy server.")
        else:
            return await ctx.author.send("Cancelled. Your profile was not modified.")

    @profilesettings.command(name="apexm")
    async def setup_apexm(self,ctx):
        """Set up your Apex Legends Profile."""
        currAPEX = await self.config.user(ctx.author).apexmobile()

        await ctx.send(f"{ctx.author.mention} I will DM you to continue the set up process. Please ensure your DMs are open!")
        await ctx.author.send("Hello! Let's set up your Apex Legends profile in Ataraxy.\n\nSend any message to get started.")

        def dm_check(m):
            return m.author == ctx.author and m.guild is None

        try:
            startmsg = await ctx.bot.wait_for("message", timeout=60, check=dm_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")

        def confirm_check(m):
            return m.author == ctx.author and m.guild is None and (m.content.lower() == "yes" or m.content.lower() == "no")

        await ctx.author.send(f"```What's your in-game name (IGN)? Please do not put your User ID.```")
        try:
            ign = await ctx.bot.wait_for("message", timeout=60)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")
        ign = ign.content

        embed = await profile_embed(ctx=ctx,
                    message=f"**Please confirm your entries below. You will need to start over if any are incorrect.**\n\nRespond with `yes` or `no` to confirm.",
                    show_author=True)      
        embed.add_field(
            name=f"In-Game Name (IGN)",
            value=f"{ign}",
            inline=False)
        await ctx.author.send(embed=embed)

        try:
            confirm = await ctx.bot.wait_for("message", timeout=60, check=confirm_check)
        except asyncio.TimeoutError:
            return await ctx.author.send("Sorry, you timed out. Restart the process from the Ataraxy server.")

        if confirm.content.lower() == "yes":
            apexData = [
                {
                    "ign": ign,
                    }
                ]
            await self.config.user(ctx.author).apexmobile.set(apexData)
            return await ctx.author.send("Your Apex Legends Mobile profile is now set up! You can view it from the Ataraxy server.")
        else:
            return await ctx.author.send("Cancelled. Your profile was not modified.")

    @commands.command(name="whois")
    async def user_info(self, ctx: commands.Context, user: discord.Member = None):
        """Show your profile, or that of another user."""

        if user is None:
            user = ctx.author

        if user.bot:
            return

        embed = await profile_embed(
            ctx=ctx,
            message=f"Fetching data... please wait.")
        init_message = await ctx.send(embed=embed)

        mee6cog = ctx.bot.get_cog("Mee6Rank")
        clashcog = ctx.bot.get_cog("ClashOfClans")

        nameSet = await self.config.user(user).name()
        ageSet = await self.config.user(user).age()
        locationSet = await self.config.user(user).location()
        userStatementSet = await self.config.user(user).statement()
        codmSet = await self.config.user(user).codm()
        apexMobileSet = await self.config.user(user).apexmobile()
        
        embedpaged = []        

        if user.premium_since:
            booster_timediff = datetime.datetime.now() - user.premium_since
            booster_desc = f"Server Boosting since **{booster_timediff.days} day(s)** ago.\n\u200b\n"
        else:
            booster_desc = ""
        
        if userStatementSet == "":
            userStatement = "\n\u200b\n*You can include a personal message here for Ataraxy. Set up your profile with `;myinfo setup`.*"
        else:
            userStatement = f"\n\u200b\n*{userStatementSet}*"

        discordEmbed = await profile_embed(ctx=ctx,
                    title=f"{user.name}#{user.discriminator}'s Ataraxy Profile",
                    message=f"{user.mention}{userStatement}\n\u200b",
                    show_author=True)
        discordEmbed.set_thumbnail(url=user.avatar_url)

        if nameSet:
            discordEmbed.add_field(
                name=f"You may call me...",
                value=f"{nameSet}",
                inline=True)
        if ageSet:
            discordEmbed.add_field(
                name=f"My age",
                value=f"{ageSet}",
                inline=True)
        if locationSet:
            discordEmbed.add_field(
                name=f"I live in...",
                value=f"{locationSet}",
                inline=True)

        try:
            mee6user = await Mee6Rank._get_player(mee6cog, user, get_avatar=False)
        except:
            mee6user = None

        if mee6user:
            discordEmbed.add_field(
                name=f"**__Discord__**",
                value=f"{booster_desc}Rank: **{mee6user.rank}**\u3000Level: **{mee6user.level}**\u3000XP: **{numerize.numerize(mee6user.level_xp,2)}** / {numerize.numerize(mee6user.level_total_xp,2)}\n*Find the Server Leaderboard at https://mee6.gg/ataraxy.*",
                inline=False)
        else:
            discordEmbed.add_field(
                name=f"**__Discord__**",
                value=f"*The Discord Leaderboard service isn't available right now.*\n\u200b\n",
                inline=False)

        medals = ""
        for role in user.roles:
            if role.id == 761785109321744437 or role.id == 669682394495975424:
                medals += f"<@&{role.id}> "

        if not medals:
            medals = "We couldn't find anything here :(."

        discordEmbed.add_field(
            name=f"**Community Medals**",
            value=f"{medals}",
            inline=False)

        joined_timediff = datetime.datetime.now() - user.joined_at
        registered_timediff = datetime.datetime.now() - user.created_at

        discordEmbed.add_field(
            name=f"**Joined {user.guild}**",
            value=f"{user.joined_at.strftime('%b %d, %Y')}\n{joined_timediff.days} day(s) ago",
            inline=True)

        discordEmbed.add_field(
            name=f"**First seen on Discord**",
            value=f"{user.created_at.strftime('%b %d, %Y')}\n{registered_timediff.days} day(s) ago\n\u200b",
            inline=True)

        clashAccounts = []
        clashMember = None

        try:
            clashTags = await clashcog.config.user(user).players()
        except:
            clashTags = []

        if len(clashTags) > 0:
            for tag in clashTags:
                try:
                    player = Member(ctx,tag)
                except:
                    pass
                else:
                    clashAccounts.append(player)
                    if not clashMember:
                        if player.atxMemberStatus == 'member':
                            clashMember = "Member"
                        if player.atxRank != 'none':
                            clashMember = player.atxRank
                    elif clashMember == 'member':
                        if player.atxRank != 'none':
                            clashMember = player.atxRank

            if clashMember:
                clashMemberDesc = f"{clashMember} of Ataraxy Clash of Clans"
            else:
                clashMemberDesc = "**Join an Ataraxy Clan with one of your accounts to be a member!**"

            if len(clashAccounts) > 0:
                discordEmbed.add_field(
                    name=f"**__Clash Of Clans__**",
                    value=f"**{clashMemberDesc}**\n*Only your top 3 accounts, ranked by XP, are shown here. Update your Clash profile in <#803655289034375178>.*",
                    inline=False)
                
                discordEmbed.set_thumbnail(url=user.avatar_url)

                clashAccounts.sort(key=lambda x:(x.exp,x.homeVillage['townHall']['thLevel']),reverse=True)

                for player in clashAccounts[:3]:
                    try:
                        if player.atxMemberStatus == 'member':
                            clan_description = f"[{player.clan['clan_info']['name']}](https://www.clashofstats.com/clans/{player.clan['clan_info']['tag'].replace('#','')})"
                        else:
                            clan_description = f"{player.clan['role']} of [{player.clan['clan_info']['name']}](https://www.clashofstats.com/clans/{player.clan['clan_info']['tag'].replace('#','')})"
                    except:
                        clan_description = "No Clan"

                    accountDesc = f"\u200b\u3000<:Exp:825654249475932170> {player.exp}\u3000{th_emotes[player.homeVillage['townHall']['thLevel']]} {player.homeVillage['townHall']['discordText']}\u3000<:Clan:825654825509322752> {clan_description}\n"

                    discordEmbed.add_field(
                        name=f"**{player.player}** ({player.tag})",
                        value=f"{accountDesc}",
                        inline=False)

        if len(codmSet) > 0:
            discordEmbed.add_field(
                name=f"**__Call of Duty: Mobile__**",
                value=f"\u200b\u3000Server: **{codmSet[0]['server']}**\n\u200b\u3000IGN: **{codmSet[0]['ign']}**",
                inline=False)

        if len(apexMobileSet) > 0:
            discordEmbed.add_field(
                name=f"**__Apex Legends Mobile__**",
                value=f"\u200b\u3000IGN: **{apexMobileSet[0]['ign']}**",
                inline=False)

        if user == ctx.author:
            discordEmbed.add_field(
                name=f"\u200b",
                value=f"*Use the commands in `;myinfo` to update your information on this page, except for Clash Of Clans.*",
                inline=False)
                
        await ctx.send(embed=discordEmbed)
        return await init_message.delete()