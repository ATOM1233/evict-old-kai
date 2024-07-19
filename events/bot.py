import discord, datetime, logging
from discord.ext import commands, tasks
from discord import Embed

@tasks.loop(seconds=5)
async def servers_check(bot: commands.Bot):
    return [await guild.leave() for guild in bot.guilds if guild.id not in [x['guild_id'] for x in await bot.db.fetch("SELECT guild_id FROM authorize")]]

class Bot(commands.Cog): 
    def __init__(self, bot: commands.Bot):
      self.bot = bot
      
    @commands.Cog.listener()
    async def on_ready(self): 
        servers_check.start(self.bot)
        
    @commands.Cog.listener('on_guild_join')
    async def join_log(self, guild: discord.Guild):
            channel_id = 1262304011562782804
            channel = self.bot.get_channel(channel_id)
     
            icon= f"[icon]({guild.icon.url})" if guild.icon is not None else "N/A"
            splash=f"[splash]({guild.splash.url})" if guild.splash is not None else "N/A"
            banner=f"[banner]({guild.banner.url})" if guild.banner is not None else "N/A"   
            embed = discord.Embed(color=self.bot.color, timestamp=datetime.datetime.now(), description=f"evict has joined a guild.")   
            embed.set_thumbnail(url=guild.icon)
            embed.set_author(name=guild.name, url=guild.icon)
            embed.add_field(name="Owner", value=f"{guild.owner.mention}\n{guild.owner}")
            embed.add_field(name="Members", value=f"**Users:** {len(set(i for i in guild.members if not i.bot))} ({((len(set(i for i in guild.members if not i.bot)))/guild.member_count) * 100:.2f}%)\n**Bots:** {len(set(i for i in guild.members if i.bot))} ({(len(set(i for i in guild.members if i.bot))/guild.member_count) * 100:.2f}%)\n**Total:** {guild.member_count}")
            embed.add_field(name="Information", value=f"**Verification:** {guild.verification_level}\n**Boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**Large:** {'yes' if guild.large else 'no'}")
            embed.add_field(name="Design", value=f"{icon}\n{splash}\n{banner}")
            embed.add_field(name=f"Channels ({len(guild.channels)})", value=f"**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}\n**Categories** {len(guild.categories)}")
            embed.add_field(name="Counts", value=f"**Roles:** {len(guild.roles)}/250\n**Emojis:** {len(guild.emojis)}/{guild.emoji_limit*2}\n**Stickers:** {len(guild.stickers)}/{guild.sticker_limit}")
            embed.set_footer(text=f"Guild ID: {guild.id}")
            if guild.banner:
                embed.set_image(url=guild.banner)
            try: await channel.send(embed=embed)
            except: return

    @commands.Cog.listener('on_guild_remove')
    async def leave_log(self, guild: discord.Guild):
            channel_id = 1262304011562782804
            channel = self.bot.get_channel(channel_id)
     
            icon= f"[icon]({guild.icon.url})" if guild.icon is not None else "N/A"
            splash=f"[splash]({guild.splash.url})" if guild.splash is not None else "N/A"
            banner=f"[banner]({guild.banner.url})" if guild.banner is not None else "N/A"   
            embed = discord.Embed(color=self.bot.color, timestamp=datetime.datetime.now(), description=f"evict has left a guild.")   
            embed.set_thumbnail(url=guild.icon)
            embed.set_author(name=guild.name, url=guild.icon)
            embed.add_field(name="Owner", value=f"{guild.owner.mention}\n{guild.owner}")
            embed.add_field(name="Members", value=f"**Users:** {len(set(i for i in guild.members if not i.bot))} ({((len(set(i for i in guild.members if not i.bot)))/guild.member_count) * 100:.2f}%)\n**Bots:** {len(set(i for i in guild.members if i.bot))} ({(len(set(i for i in guild.members if i.bot))/guild.member_count) * 100:.2f}%)\n**Total:** {guild.member_count}")
            embed.add_field(name="Information", value=f"**Verification:** {guild.verification_level}\n**Boosts:** {guild.premium_subscription_count} (level {guild.premium_tier})\n**Large:** {'yes' if guild.large else 'no'}")
            embed.add_field(name="Design", value=f"{icon}\n{splash}\n{banner}")
            embed.add_field(name=f"Channels ({len(guild.channels)})", value=f"**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}\n**Categories** {len(guild.categories)}")
            embed.add_field(name="Counts", value=f"**Roles:** {len(guild.roles)}/250\n**Emojis:** {len(guild.emojis)}/{guild.emoji_limit*2}\n**Stickers:** {len(guild.stickers)}/{guild.sticker_limit}")
            embed.set_footer(text=f"Guild ID: {guild.id}")
            if guild.banner:
                embed.set_image(url=guild.banner)
            try: await channel.send(embed=embed)
            except: return
      
    @commands.Cog.listener('on_guild_join')
    async def join_message(self, guild: discord.Guild):
        
        check = await self.bot.db.fetchrow("SELECT * FROM gblacklist WHERE guild_id = {}".format(guild.id))
        check1 = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = {}".format(guild.id))
        
        if check1 is None: return
        if check: return
        
        if channel := discord.utils.find(
            lambda c: c.permissions_for(guild.me).embed_links, guild.text_channels
        ):
        
            
            embed = Embed(
                color=self.bot.color,
                title="Getting started with evict",
                description=(
                    "Hey! Thanks for your interest in **evict bot**. "
                    "The following will provide you with some tips on how to get started with your server!"
                ),
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar)

            embed.add_field(
                name="**Prefix 🤖**",
                value=(
                    "The most important thing is my prefix. "
                    f"It is set to `;` by default for this server and it is also customizable, "
                    "so if you don't like this prefix, you can always change it with `prefix` command!"
                ),
                inline=False,
            )
            embed.add_field(
                name="**Moderation System 🛡️**",
                value=(
                    "If you would like to use moderation commands, such as `jail`, `ban`, `kick` and so much more... "
                    "please run the `setmod` command to quickly set up the moderation system."
                ),
                inline=False,
            )
            embed.add_field(
                name="**Documentation and Help 📚**",
                value=(
                    "You can always visit our [documentation](https://docs.evict.cc)"
                    " and view the list of commands that are available [here](https://evict.cc/commands)"
                    " - and if that isn't enough, feel free to join our [Support Server](https://discord.gg/evict) for extra assistance!"
                ),
            )
            
            await channel.send(embed=embed)

    @commands.Cog.listener('on_guild_join')
    async def gblacklist_check(self, guild: discord.Guild):
        
        check = await self.bot.db.fetchrow("SELECT * FROM gblacklist WHERE guild_id = {}".format(guild.id))
        
        if check is not None:
            await guild.leave()
            
    @commands.Cog.listener('on_guild_join')
    async def authorization_check(self, guild: discord.Guild):
        
        check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = {}".format(guild.id))
        
        if check: return
        
        if channel := discord.utils.find(
            lambda c: c.permissions_for(guild.me).embed_links, guild.text_channels):
        
            if check is None:
                embed = Embed(
                color=self.bot.color,
                description=(
                    "Hey! Evict is authorization only, please join the [support server](https://discord.gg/evict)"
                    " and request a whitelist."))
        
            await channel.send(embed=embed)
            await guild.leave()
            
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        channel_id = 1262304000041025609
        channel = self.bot.get_channel(channel_id)
        embed = discord.Embed(description=f"Text command ``{ctx.command.qualified_name}`` has been ran in ``{ctx.guild} ({ctx.guild.id})`` by ``{ctx.author} ({ctx.author.id})`` with message id: ``{ctx.message.id}``.", color=self.bot.color)
        try: await channel.send(embed=embed)
        except: return

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error: commands.CommandError):
        channel_id = 1262303993439326208
        channel = self.bot.get_channel(channel_id)
        embed = discord.Embed(description=f"Text command ``{ctx.command.qualified_name}`` has ran into an error in ``{ctx.guild} ({ctx.guild.id})`` by ``{ctx.author} ({ctx.author.id})`` with message id: ``{ctx.message.id}``. \n\n **Error: {error}**", color=self.bot.color)
        try: await channel.send(embed=embed)
        except: return

async def setup(bot: commands.Bot) -> None: 
  await bot.add_cog(Bot(bot)) 