import discord
from discord.ext import commands
from patches.permissions import Permissions

class moderation(commands.Cog):
   def __init__(self, bot: commands.Bot):
       self.bot = bot

   @commands.command(description='ban members from your server', brief='ban members', usage='[member] [reason]')
   @Permissions.has_permission(ban_members=True)
   async def ban(self, ctx: commands.Context, user: discord.User, reason:str="No reason provided"):
       if not Permissions.check_hierarchy(self.bot, ctx.author, user): return await ctx.warning(f"You cannot kick*{user.mention}")
       await ctx.guild.ban(user=user, reason=reason + " | {}".format(ctx.author))
       await ctx.success(f"successfully banned **{user}**.")

   @commands.command(description='kick members from your server', brief='kick members', usage='[member] [reason]')
   @Permissions.has_permission(kick_members=True)
   async def kick(self, ctx: commands.Context, user: discord.Member, reason:str="No reason provided"):
       if not Permissions.check_hierarchy(self.bot, ctx.author, user): return await ctx.warning(f"You cannot kick*{user.mention}")
       await ctx.guild.kick(user=user, reason=reason + " | {}".format(ctx.author))
       await ctx.success(f"successfully kicked **{user}**.")

async def setup(bot) -> None:
    await bot.add_cog(moderation(bot))