from discord.ext import commands
import discord

OWNERS = [214753146512080907]
  
class Permissions:
    
    def has_permission(**perms: bool) -> commands.check:
        
        invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
        if invalid:
            raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

        def predicate(ctx: commands.Context) -> bool:
            
            permissions = ctx.permissions
            
            if discord.Permissions.administrator in permissions: return True
            
            missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

            if ctx.author.id in ctx.bot.owner_ids or not missing: return True

            raise commands.MissingPermissions(missing)

        return commands.check(predicate)
    
    def check_hierarchy(bot: commands.AutoShardedBot, author: discord.Member, target: discord.Member):
        if target.id in OWNERS: raise commands.CommandInvokeError("You cannot perform this action on a bot owner.")
        if author.id in bot.owner_ids: return True
        if target.id == author.id: raise commands.CommandInvokeError("You cannot perform this action on yourself.")
        if target.id == author.guild.owner.id: raise commands.CommandInvokeError("You cannot perform this action on the server owner.")
        if target.top_role >= author.top_role: raise commands.CommandInvokeError("You cannot perform this action on a higher role than you.")
        if target.id in bot.owner_ids: raise commands.CommandInvokeError("You cannot perform this action on a bot owner.")
        return True
    
    def server_owner():
     
     async def server_owner(ctx: commands.Context):
            if ctx.author.id == ctx.guild.owner_id: return True
            if ctx.author.id in OWNERS: return True
            else: raise commands.CommandInvokeError("You need to be the server owner to run this command.")
     
     return commands.check(server_owner)
        
    def booster():
     
     async def booster(ctx: commands.Context):
            che = await ctx.bot.db.fetchrow("SELECT * FROM booster_module WHERE guild_id = {}".format(ctx.guild.id))
            if che is None: raise commands.CommandInvokeError("the booster role module is **not** configured.")
            check = await ctx.bot.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(ctx.guild.id, ctx.author.id))
            if check is None: raise commands.CommandInvokeError("You don't have a booster role.")
     
     return commands.check(booster)
    
    def donor():
     
     async def donor(ctx: commands.Context):
            if ctx.command.name in ["hardban", "uwulock", "unhardban"]: 
                if ctx.author.id == ctx.guild.owner_id: return True
                if ctx.author.id in OWNERS: return True
            check = await ctx.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = {}".format(ctx.author.id))              
            if check is None: raise commands.CommandInvokeError("You need to be a donor to run this command.")
     
     return commands.check(donor)