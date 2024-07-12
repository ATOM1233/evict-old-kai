import discord, os, sys
from discord.ext import commands

class PaginatorView(discord.ui.View): 
    def __init__(self, ctx: commands.Context, embeds: list): 
      super().__init__()  
      self.embeds = embeds
      self.ctx = ctx
      self.i = 0
     
    @discord.ui.button(emoji="<:left:1259608758800220251>", style=discord.ButtonStyle.secondary)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.warning(interaction, "You are not the author of this embed")          
      if self.i == 0: 
        await interaction.response.edit_message(embed=self.embeds[-1])
        self.i = len(self.embeds)-1
        return
      self.i = self.i-1
      return await interaction.response.edit_message(embed=self.embeds[self.i])

    @discord.ui.button(emoji="<:right:1259608897308721152>", style=discord.ButtonStyle.secondary)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.warning(interaction, "You are not the author of this embed")     
      if self.i == len(self.embeds)-1: 
        await interaction.response.edit_message(embed=self.embeds[0])
        self.i = 0
        return 
      self.i = self.i + 1  
      return await interaction.response.edit_message(embed=self.embeds[self.i])   
    
    @discord.ui.button(emoji="<:false:1259606495234887740>", style=discord.ButtonStyle.secondary)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button): 
      if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.warning(interaction, "You are not the author of this embed")     
      await interaction.message.delete()

    async def on_timeout(self) -> None: 
        mes = await self.message.channel.fetch_message(self.message.id)
        if mes is None: return
        if len(mes.components) == 0: return
        for item in self.children:
            item.disabled = True

        try: await self.message.edit(view=self)   
        except: pass

class StartUp:

 async def startup(bot):
    await bot.wait_until_ready()

 async def loadcogs(self): 
  
  for file in os.listdir("./events"): 
   if file.endswith(".py"):
    try:
     await self.load_extension(f"events.{file[:-3]}")
     print(f"Loaded plugin {file[:-3]}".lower())
    except Exception as e: print("failed to load %s %s".lower(), file[:-3], e)
  
  for fil in os.listdir("./cogs"):
   if fil.endswith(".py"):
    try:
     await self.load_extension(f"cogs.{fil[:-3]}")
     print(f"Loaded plugin {fil[:-3]}".lower())
    except Exception as e: print("failed to load %s %s".lower(), fil[:-3], e)
    
 async def identify(self):
    payload = {
        'op': self.IDENTIFY,
        'd': {
            'token': self.token,
            'properties': {
                '$os': sys.platform,
                '$browser': 'Discord iOS',
                '$device': 'Discord iOS',
                '$referrer': '',
                '$referring_domain': ''
            },
            'compress': True,
            'large_threshold': 250,
            'v': 3
        }
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload['d']['presence'] = {
            'status': state._status,
            'game': state._activity,
            'since': 0,
            'afk': False
        }

    if state._intents is not None:
        payload['d']['intents'] = state._intents.value

    await self.call_hooks('before_identify', self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)