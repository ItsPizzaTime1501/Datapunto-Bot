import discord
import typing 
import datetime
import time
import re
import pyqrcode
import random
import os
import sys

from pyqrcode import QRCode
from cogs.checks import is_admin, check_admin, check_bot_or_admin, prompt
from discord.ext import commands, menus
from subprocess import call

class Test(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sdroot(self, ctx):

       print(f'Sugma')

       embed = discord.Embed()
       embed.set_image(url="https://i.imgur.com/pVS2Lc6.png")
       await ctx.send(embed=embed)

    @commands.command()
    async def dver(self, ctx):

        output = printf(discord.__version__)
        await ctx.send(f"{output}")

    @is_admin("Admin")
    @commands.command(aliases=["hidechannel"])
    async def hide(self,ctx,channels: commands.Greedy[discord.TextChannel]):
        """Hides a channel from everyone's sight. Bot-Admin only."""
        author = ctx.author
        if not channels:
            channels.append(ctx.channel)
        hidden = []
        for c in channels:
            if c.overwrites_for(ctx.guild.default_role).read_messages is False:
                await ctx.send(f"🙈️ {c.mention} is already hidden. Use `n!unhide` to unlock.")
                continue
            try:
                await c.set_permissions(ctx.guild.default_role, read_messages=False)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
            await c.send("🙈️ Channel hidden.")
            hidden.append(c)

    @is_admin("Admin")
    @commands.command(aliases=["unhidechannel", "showchannel"])
    async def unhide(self,ctx,channels: commands.Greedy[discord.TextChannel]):
        """Unhides a channel from everyone's sight. Bot-Admin only."""
        author = ctx.author
        if not channels:
            channels.append(ctx.channel)
        unhidden = []
        for c in channels:
            if c.overwrites_for(ctx.guild.default_role).read_messages is None:
                await ctx.send(f"🧐️ {c.mention} is already unhidden. Use `n!hide` to hide.")
                continue
            try:
                await c.set_permissions(ctx.guild.default_role, read_messages=None)
            except discord.errors.Forbidden:
                await ctx.send("💢 I don't have permission to do this.")
            await c.send("🧐️ Channel unhidden.")
            unhidden.append(c)

    @commands.command()
    async def move(self,ctx,channels: commands.Greedy[discord.TextChannel], *, category: discord.CategoryChannel.name):

        await ctx.send(category.id)
        
#        if {category} & {x.id for x in ctx.guild.categories}:
#            for i in channels:
#                if {i.category_id} & {category}:
#                    await ctx.send(f"{i.category_id}\n<#{i.category_id}>")
#                    await ctx.send("Valid ID but why are you trying to move them where they already are?")
#                    return
#                else:
#                    pass
#    
#            else:
#                await ctx.send("Valid ID and different category")
#                for i in channels:
#                    await ctx.send(str(category))
#                    await i.edit(category=str(category))
#        else:
#            await ctx.send("Not a valid category ID")

    #    for x in ctx.guild.categories:
    #        await ctx.send(f"{x.name}\n")
    #    if not channels:
    #        await ctx.send("Fuck you on about")
        

    @commands.guild_only()
    @commands.command()
    async def slowmode(self, ctx, time, channel: discord.TextChannel=None):
        """Apply a given slowmode time to a channel.
        
        The time format is identical to that used for timed kicks/bans/takehelps.
        It is not possible to set a slowmode longer than 6 hours.
        
        Staff only."""
        if not channel:
            channel = ctx.channel

        units = { # This bit is copied from kickban, removed days since it's not needed.
            "d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1
        }
        seconds = 0
        match = re.findall("([0-9]+[smhd])", time)
        if not match:
            return await ctx.send("💢 I don't understand your time format.")
        for item in match:
            seconds += int(item[:-1]) * units[item[-1]]
        if seconds > 21600:
            return await ctx.send("💢 You can't slowmode a channel for longer than 6 hours!")
        try:
            await channel.edit(slowmode_delay=seconds)
        except discord.errors.Forbidden:
            return await ctx.send("💢 I don't have permission to do this.")
        msg = f"🕙 **Slowmode**: {ctx.author.mention} set a slowmode delay of {time} ({seconds}) in {ctx.channel.mention}"
        await self.bot.channels["modlogs"].send(msg)

    @is_admin("Test-Admin")
    @commands.command()
    async def special(self, ctx):
        
        await ctx.send("You're specialllll!")

    @commands.command()
    async def listchans(self, ctx):
    
        await ctx.send("{guild.channels}")

    @commands.command()
    async def attach(self, ctx):
        if ctx.message.attachment:
            await ctx.send("That's not attached, right?")
        else:
            await ctx.send("attached or you're just bad at python, glazed")

    @commands.command(aliases=["dump", "parser", "dumpparser"])
    async def crash(self, ctx, url=""):
        if ctx.message.attachments:
            a = ctx.message.attachments[0]
            if a.filename.lower().endswith('.dmp'):
                url = a.url
                pass
            else:
                await ctx.send("Not a valid .dmp file")

        if not url == "":
            tmp = await ctx.channel.send("Parsing in progress")
            file_resp = await self.bot.aiosession.get(url)
            file = await file_resp.read()
            with open("dump.dmp", "wb") as f:
                f.write(file)
            parse_output = await self.bot.async_call_shell(f"{sys.executable} utils/dump_parser.py dump.dmp")
            await ctx.send(f"```{parse_output[7:]}```")
            await tmp.delete()
            await self.bot.async_call_shell("rm dump.dmp")
        else:
            await ctx.channel.send("No attachments or URL")

    @commands.command()
    async def qrcode(self, ctx, *, message):
#        link = "https://glazedbelmont.github.io/"
        url = pyqrcode.create(message)
        url.svg("qr.svg", scale = 8)
        file = discord.File("/home/glazed/DatapuntoBot/qr.svg", filename="qr.svg")
        embed = discord.Embed()
        embed.set_image(url=file)
        await ctx.send(embed=embed)

    @commands.command()
    async def admincheck(self, ctx):
        admin_roles = ['Bot-Admin', 'Admin', 'Test-Admin']
        userroles = (x.name for x in ctx.author.roles)
        msg = "```"
        for item in userroles:
            for item1 in admin_roles:
                if item == item1:
                    msg += f"\n{item}"
                    await ctx.send("Permission granted")
                    msg += "```"
                    await ctx.send(msg)
                    return
                else:
                    pass
        msg += "```"
        
        await ctx.send("You don't seem to have the required roles.")

    @commands.command()
    async def emojicheck(self, ctx, emoji: discord.Emoji):
        msg = ""
        msg += f"{emoji}"
        msg += f"\nName: `{emoji.name}`"
        msg += f"\nID: `{emoji.id}`"
        msg += f"\nAnimated: `{emoji.animated}`"
        msg += f"\nGuild: `{emoji.guild}`"
        msg += f"\nURL: `{emoji.url}`"
        msg += f"\nShitty d.py string: `<:{emoji.name}:{emoji.id}>`"
        msg += ""
        await ctx.send(msg)

    @commands.command()
    async def whohas(self, ctx,*, role: discord.Role):
        if role == ('@everyone' or '554178232531025940'):
            await ctx.send("Nice try :P")
            return

        members = []

        for member in ctx.guild.members:
            if role in member.roles:
                members.append(member.name)
        if members == []:
            await ctx.send('`Nobody has that role.`')
        else:
            members.sort(key=str.casefold)
            msg = f"``The following members have the {role.name} role:\n"
            for x in members:
                msg += f"{x}\n"
            msg += f"[{len(members)}]"
            msg += "``"
            await ctx.send(msg)

    @commands.command()
    async def err(self, ctx):
        try:
            await ctx.channel.send(content=f"Build completed.", file=discord.File(f'{self.bot.home_path}/tmp_compile/{name}/{name}.zip'))
        except FileNotFoundError:
            await ctx.send(f'`{self.bot.home_path}/tmp_compile/{name}/{name}.zip` does not exist.')
        finally:
            await self.bot.change_presence(status="online")
#        await ctx.send(the_void)



    

    @commands.Cog.listener()
    async def on_message(self, message):
#        await message.add_reaction("<:wagu:686742849777303570>")
        if re.search("wagu", message.content.lower()):
            await message.add_reaction("<:wagu:686742849777303570>")
        else:
            return
#        konami_code = ":3ds_dpad_up: :3ds_dpad_up: :3ds_dpad_down: :3ds_dpad_down: :3ds_dpad_left: :3ds_dpad_right: :3ds_dpad_left: :3ds_dpad_right: :3ds_button_b: :3ds_button_a:"
#        walnut = re.fullmatch(konami_code, message.content.lower())
#        if isinstance(message.channel, discord.abc.PrivateChannel):
#            return
#        if message.author == message.guild.me: # don't process messages by the bot or staff or in the helpers channel
#            return
#        if message.guild == self.bot.get_guild(554178232531025940): # Don't give a gun to a kid
#            return
#        if walnut is not None:
#            await message.channel.send("yeah no, muted")
#        else:
#            await message.channel.send(message.content)
#            return
#            await message.channel.send("sad trumper")
        

def setup(bot):
    bot.add_cog(Test(bot))
