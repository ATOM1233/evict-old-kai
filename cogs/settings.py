from discord.ext import commands
from patches.permissions import Permissions

class settings(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
    @commands.group(invoke_without_command=True, description='server settings', brief='manage guild', aliases=['config'])
    @Permissions.has_permission(manage_guild=True)
    async def settings(self, ctx: commands.Context):
        await ctx.create_pages()
    
    @settings.group(invoke_without_command=True, description='repost social media links as embeds', brief='manage server', aliases=['socialmedia'])
    @Permissions.has_permission(manage_guild=True)
    async def reposter(self, ctx: commands.Context):
        await ctx.create_pages()
        
    @reposter.command(description='enable reposter', brief='manage server', aliases=['true', 'on'])
    @Permissions.has_permission(manage_guild=True)
    async def enable(self, ctx: commands.Context):
        social = await ctx.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', ctx.guild.id)
        if social is not None and social['toggled']: return await ctx.warning('**Social Media** Reposting is already **enabled**.')
        await ctx.bot.db.execute("INSERT INTO settings_social VALUES ($1, $2, $3) ON CONFLICT (guild_id) DO UPDATE SET toggled = $2 WHERE settings_social.guild_id = $1", ctx.guild.id, True, 'evict')
        return await ctx.success('**social media** reposting is now enabled.')
    
    @reposter.command(description="disable reposter", brief='manage server', aliases=['false', 'off'])
    @Permissions.has_permission(manage_guild=True)
    async def disable(self, ctx: commands.Context):
        social = await ctx.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', ctx.guild.id)
        if not social or not social['toggled']: return await ctx.warning('**Social Media** Reposting is already **disabled**.')
        await ctx.bot.db.execute("INSERT INTO settings_social VALUES ($1, $2, $3) ON CONFLICT (guild_id) DO UPDATE SET toggled = $2 WHERE settings_social.guild_id = $1", ctx.guild.id, False, 'evict')
        return await ctx.success('**social media** reposting is now disabled.')
    
    @reposter.command(description="set reposter prefix (set to 'none' to have no prefix)", usage='[prefix]', brief='manage server')
    @Permissions.has_permission(manage_guild=True)
    async def prefix(self, ctx: commands.Context, prefix: str=None):
        social = await ctx.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', ctx.guild.id)
        if not social: return await ctx.warning('Social Media Reposting is not enabled.')
        if not prefix: return await ctx.success(f'Current prefix: {social["prefix"]}')
        await ctx.bot.db.execute("UPDATE settings_social SET prefix = $2 WHERE guild_id = $1", ctx.guild.id, prefix)
        return await ctx.success(f'**social media** reposting prefix is now set to `{prefix}`.')
    
async def setup(bot):
    await bot.add_cog(settings(bot))