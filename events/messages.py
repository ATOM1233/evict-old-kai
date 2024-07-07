from discord.ext import commands 
import discord, json, asyncio, datetime, re
from uwuipy import uwuipy
from discord import Embed, Message, User
from reposter.reposter import Reposter

DISCORD_API_LINK = "https://discord.com/api/invite/"

class Messages(commands.Cog): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
    
  async def webhook(self, channel) -> discord.Webhook:
      for webhook in await channel.webhooks():
        if webhook.user == self.bot.user:
          return webhook
      try: await channel.create_webhook(name='evict')
      except: pass
   
  @commands.Cog.listener('on_message')
  async def reposter(self, message: discord.Message):
        if not message.guild: return
        if message.author.bot: return
        args = message.content.split(' ')
        social = await self.bot.db.fetchrow('SELECT * FROM settings_social WHERE guild_id = $1', message.guild.id)
        
        if not social or not social['toggled']: return
        
        prefix = social['prefix']
        if prefix.lower() == 'none': return await Reposter().repost(self.bot, message, args[0])
        if args[0] == prefix and args[1] is not None: return await Reposter().repost(self.bot, message, args[1])
        
  @commands.Cog.listener()
  async def subscriber_join(self, member: discord.Member): 
    if member.guild.id == 1208651928507129887:
      check = await self.bot.db.fetchrow("SELECT * FROM authorize WHERE buyer = $1", member.id)
      if check: await member.add_roles(member.guild.get_role(1209127936414842990))

  @commands.Cog.listener('on_message')
  async def boost_listener(self, message: discord.Message): 
     if "MessageType.premium_guild" in str(message.type):
      if message.guild.id == 952161067033849919: 
       member = message.author
       check = await self.bot.db.fetchrow("SELECT * FROM donor WHERE user_id = $1", member.id)
       if check: return 
       ts = int(datetime.datetime.now().timestamp())
       await self.bot.db.execute("INSERT INTO donor VALUES ($1,$2)", member.id, ts)  
       return await message.channel.send(f"{member.mention}, enjoy your perks! <a:catclap:1081008257776226354>")     

  @commands.Cog.listener("on_message")
  async def seen_listener(self, message: discord.Message): 
      if not message.guild: return 
      if message.author.bot: return
      check = await self.bot.db.fetchrow("SELECT * FROM seen WHERE guild_id = {} AND user_id = {}".format(message.guild.id, message.author.id))
      if check is None: return await self.bot.db.execute("INSERT INTO seen VALUES ($1,$2,$3)", message.guild.id, message.author.id, int(datetime.datetime.now().timestamp()))  
      ts = int(datetime.datetime.now().timestamp())
      await self.bot.db.execute("UPDATE seen SET time = $1 WHERE guild_id = $2 AND user_id = $3", ts, message.guild.id, message.author.id)

  @commands.Cog.listener('on_message')
  async def bump_event(self, message: discord.Message): 
     if message.type == discord.MessageType.chat_input_command:
       if message.interaction.name == "bump" and message.author.id == 302050872383242240:   
        if "Bump done!" in message.embeds[0].description or "Bump done!" in message.content:
          check = await self.bot.db.fetchrow("SELECT * FROM bumps WHERE guild_id = {}".format(message.guild.id))  
          if check is not None: 
           await message.channel.send(f"{message.interaction.user.mention} thanks for bumping the server. You will be reminded in 2 hours!") 
           await asyncio.sleep(7200)
           embed = discord.Embed(color=self.bot.color, description="Bump the server using the `/bump` command")
           await message.channel.send(f"{message.interaction.user.mention} time to bump !!", embed=embed)  

  @commands.Cog.listener("on_message")
  async def afk_listener(self, message: discord.Message):
     if not message.guild: return 
     if message.author.bot: return
     if message.mentions: 
      if len(message.mentions) == 1: 
        mem = message.mentions[0]
        check = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, mem.id) 
        if check:
         em = discord.Embed(color=self.bot.color, description=f"💤 **{mem}** is AFK since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(check['time'])))}** - {check['reason']}")
         await message.reply(embed=em)
      else: 
       embeds = [] 
       for mem in message.mentions:
         check = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, mem.id) 
         if check:
          em = discord.Embed(color=self.bot.color, description=f"💤 **{mem}** is AFK since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(check['time'])))}** - {check['reason']}")
          embeds.append(em)
         if len(embeds) == 10: 
           await message.reply(embeds=embeds)
           embeds = []
       if len(embeds) > 0: await message.reply(embeds=embeds)
       embeds = []

     che = await self.bot.db.fetchrow("SELECT * from afk where guild_id = $1 AND user_id = $2", message.guild.id, message.author.id) 
     if che:
      embed = discord.Embed(color=self.bot.color, description=f"<a:wave:1020721034934104074> Welcome back **{message.author}**! You were AFK since **{self.bot.ext.relative_time(datetime.datetime.fromtimestamp(int(che['time'])))}**")
      try: await message.reply(embed=embed)
      except: pass
      await self.bot.db.execute("DELETE FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)    
    
  @commands.Cog.listener('on_message_edit')
  async def edit_snipe(self, before: discord.Message, after: discord.Message): 
     if not before.guild: return 
     if before.author.bot: return 
     await self.bot.db.execute("INSERT INTO editsnipe VALUES ($1,$2,$3,$4,$5,$6)", before.guild.id, before.channel.id, before.author.name, before.author.display_avatar.url, before.content, after.content)

  @commands.Cog.listener('on_message_delete')
  async def snipe(self, message: discord.Message):
     if not message.guild: return 
     if message.author.bot: return
     invites = ["discord.gg/", ".gg/", "discord.com/invite/"]
     if any(invite in message.content for invite in invites):
       check = await self.bot.db.fetchrow("SELECT * FROM antiinvite WHERE guild_id = $1", message.guild.id)
       if check: return

     attachment = message.attachments[0].url if message.attachments else "none"
     author = str(message.author)
     content = message.content
     avatar = message.author.display_avatar.url 
     await self.bot.db.execute("INSERT INTO snipe VALUES ($1,$2,$3,$4,$5,$6,$7)", message.guild.id, message.channel.id, author, content, attachment, avatar, datetime.datetime.now())

  @commands.Cog.listener('on_message')
  async def uwulock(self, message: discord.Message):
        if not message.guild: return
        check = await self.bot.db.fetchrow("SELECT user_id FROM uwulock WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)
        check1 = await self.bot.db.fetchrow("SELECT user_id FROM guwulock WHERE user_id = $1", message.author.id)
        if check1: return  
        if check is None or not check: return 
        uwu = uwuipy()
        uwu_message = uwu.uwuify(message.content)
        hook = await self.webhook(message.channel)
        await hook.send(
                        content=uwu_message,
                        username=message.author.display_name,
                        avatar_url=message.author.display_avatar,
                        thread=message.channel if isinstance(message.channel, discord.Thread) else discord.utils.MISSING,
                    )
        await message.delete()

  @commands.Cog.listener('on_message')
  async def guwulock(self, message: discord.Message):
        if not message.guild: return
        check1 =  await self.bot.db.fetchrow("SELECT user_id FROM uwulock WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id) 
        check = await self.bot.db.fetchrow("SELECT user_id FROM guwulock WHERE user_id = $1", message.author.id)  
        if check1: return
        if check is None or not check: return 
        uwu = uwuipy()
        uwu_message = uwu.uwuify(message.content)
        hook = await self.webhook(message.channel)
        await hook.send(
                        content=uwu_message,
                        username=message.author.display_name,
                        avatar_url=message.author.display_avatar,
                        thread=message.channel if isinstance(message.channel, discord.Thread) else discord.utils.MISSING,
                    )
        await message.delete()

  @commands.Cog.listener('on_message')
  async def on_message_shutup(self, message: discord.Message):
        if not message.guild: return
        check = await self.bot.db.fetchrow("SELECT user_id FROM shutup WHERE user_id = $1 AND guild_id = $2", message.author.id, message.guild.id)   
        if check is None or not check: return 
        try: await message.delete()
        except: pass

  @commands.Cog.listener("on_message")
  async def reposter(self, message: Message):
        if (
            message.guild
            and not message.author.bot
            and message.content.startswith("evict")
        ):
            if re.search(
                r"\bhttps?:\/\/(?:m|www|vm)\.tiktok\.com\/\S*?\b(?:(?:(?:usr|v|embed|user|video)\/|\?shareId=|\&item_id=)(\d+)|(?=\w{7})(\w*?[A-Z\d]\w*)(?=\s|\/$))\b",
                message.content[len("evict") + 1 :],
            ):
                return await self.repost_tiktok(message)

  @commands.Cog.listener('on_message')
  async def imageonly(self, message: Message):
      if not message.guild: return
      if isinstance(message.author, User): return
      if message.author.guild_permissions.manage_guild: return 
      if message.author.bot: return 
      if message.attachments: return       
      check = await self.bot.db.fetchrow("SELECT * FROM mediaonly WHERE channel_id = $1", message.channel.id)
      if check: 
        try: await message.delete()
        except: pass

  @commands.Cog.listener('on_message')
  async def sticky(self, message: discord.Message):
      if message.author.bot: return
      stickym = await self.bot.db.fetchval("SELECT key FROM stickym WHERE channel_id = $1", message.channel.id)
      if not stickym: return
    
      async for message in message.channel.history(limit=3):
        if message.author.id == self.bot.user.id: await message.delete()

      return await message.channel.send(stickym)   
        
async def setup(bot: commands.Bot):
  await bot.add_cog(Messages(bot))