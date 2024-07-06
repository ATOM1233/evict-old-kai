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
     if check is not None: return await ctx.reply(f"this server is already authorized. please use `{ctx.clean_prefix}transfer` to transfer a server authorization")
     
     await self.bot.db.execute("INSERT INTO authorize VALUES ($1,$2)", guild, buyer.id)
     await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"Added **{guild}** as an authorized server"))
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
     i=0
     k=1
     l=0
     mes = ""
     number = []
     messages = []          
     for result in results:
       
      mes = f"{mes}`{k}` `{result['guild_id']}`"
      k+=1
      l+=1
      if l == 10:
       messages.append(mes)
       number.append(discord.Embed(color=self.bot.color, title=f"owned servers ({len(results)})", description=messages[i]))
       i+=1
       mes = ""
       l=0
    
     messages.append(mes)
     number.append(discord.Embed(color=self.bot.color, title=f"owned servers ({len(results)})", description=messages[i]))
     await ctx.paginator(number) 

    @commands.command()
    @commands.is_owner()
    async def unauthorize(self, ctx: commands.Context, id:int=None): 
        check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE guild_id = $1", id)
        if check is None: return await ctx.warning(f"**unable** to find this server.")
        await self.bot.db.execute("DELETE FROM authorize WHERE guild_id = $1", id)
        await ctx.success(f"**unauthorized** **{id}**")

async def setup(bot): 
    await bot.add_cog(auth(bot))    
