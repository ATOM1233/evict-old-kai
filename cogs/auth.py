import discord
from discord.ext import commands
from typing import Union

class auth(commands.Cog): 
    def __init__(self, bot: commands.Bot): 
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def authorize(self, ctx: commands.Context, guild: int, buyer: Union[discord.Member, discord.User]): 
     
     check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1", guild)
     if check is not None: return await ctx.warning("this server is **already** whitelisted.")
     
     await self.bot.db.execute("INSERT INTO authorize VALUES ($1,$2)", guild, buyer.id)
     await ctx.success(f"added **{guild}** as an authorized server to {buyer}.")
     
     view = discord.ui.View()
     view.add_item(discord.ui.Button(label="invite", url=discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions.all())))
     
     try: await buyer.send(f"Congratulations! Your server **{guild}** has been authorized.", view=view)
     except: pass
     
    @commands.command()
    @commands.is_owner()
    async def authorizeall(self, ctx: commands.Context): 
        
        for g in self.bot.guilds:
            await self.bot.db.execute("INSERT INTO authorize values ($1, $2) ON CONFLICT (guild_id) DO NOTHING", g.id, g.owner.id)
        
        embed = discord.Embed(color=self.bot.color, description=f"{ctx.author.mention}: authorizing **all** servers.")
        message = await ctx.reply(embed=embed)
        
        await message.edit(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: authorized **all** servers."))
     
    @commands.command()
    @commands.is_owner()
    async def getauth(self, ctx: commands.Context, *, member: discord.User): 
     
     results = await self.bot.db.fetch("SELECT * FROM authorize WHERE buyer = $1", member.id)
     if len(results) == 0: return await ctx.warning("no server authorized for **{}**".format(member))

     await ctx.paginate([f"{f'**{str(self.bot.get_guild(m[0]))}** `{m[0]}`' if self.bot.get_guild(m[0]) else f'`{m[0]}`'}" for m in results],
            f"Authorized guilds ({len(results)})",
            {"name": member.name, "icon_url": member.display_avatar.url})

    @commands.command()
    @commands.is_owner()
    async def unauthorize(self, ctx: commands.Context, id:int=None): 
        
        check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1", id)
        if check is None: return await ctx.warning(f"**unable** to find this server.")
        
        await self.bot.db.execute("DELETE FROM authorize WHERE guild_id = $1", id)
        await ctx.success(f"**unauthorized** **{id}**")

async def setup(bot): 
    await bot.add_cog(auth(bot))    
