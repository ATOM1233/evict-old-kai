import discord, datetime
from discord.ext import commands

class Bot(commands.Cog): 
    def __init__(self, bot: commands.Bot):
      self.bot = bot
      
    """@commands.Cog.listener('on_guild_join')
    async def auth_check(self, guild: discord.Guild):
        check = await self.bot.db.execute("SELECT * FROM authorize WHERE guild_id = $1", guild.id)
        if check is None: await guild.leave()"""

    @commands.Cog.listener('on_guild_join')
    async def join_log(self, guild: discord.Guild):
            channel_id = 1250412060760871016
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
            channel_id = 1250412060760871016
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

async def setup(bot: commands.AutoShardedBot) -> None: 
  await bot.add_cog(Bot(bot)) 