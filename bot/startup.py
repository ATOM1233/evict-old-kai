from discord.ext import commands
from events.tasks import servers_check

class startup(commands.Cog): 
    def __init__(self, bot: commands.Bot): 
      self.bot = bot 
      
    @commands.Cog.listener()
    async def on_ready(self): 
        servers_check.start(self.bot)

async def setup(bot): 
    await bot.add_cog(startup(bot))