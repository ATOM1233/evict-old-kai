import discord, Paginator
from discord.ext.commands import Context 
from discord import Embed, utils
from typing import Any, Union, Dict, Optional, List, Sequence
from bot.utils import PaginatorView
from discord.ui import View
from discord.ext import commands

class EvictContext(Context): 
  flags: Dict[str, Any] = {}
  
  async def getprefix(bot, message):
       
       if not message.guild: return ";"
       
       check = await bot.db.fetchrow("SELECT * FROM selfprefix WHERE user_id = $1", message.author.id) 
       if check: selfprefix = check["prefix"]
       
       res = await bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", message.guild.id) 
       if res: guildprefix = res["prefix"]
       
       else: guildprefix = ";"    
       
       if not check and res: selfprefix = res["prefix"]
       elif not check and not res: selfprefix = ";"
       
       return guildprefix, selfprefix 

  def find_role(self, name: str): 
   
   for role in self.guild.roles:
    
    if role.name == "@everyone": continue  
    
    if name.lower() in role.name.lower(): return role 
   return None 
 
  async def success(self, message: str) -> discord.Message:  
    return await self.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {self.author.mention}: {message}") )
 
  async def error(self, message: str) -> discord.Message: 
    return await self.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {self.author.mention}: {message}") ) 
 
  async def warning(self, message: str) -> discord.Message: 
    return await self.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {self.author.mention}: {message}") )
  
  async def create_pages(self): 
   embeds = []
   
   i=0
   
   for command in self.command.commands: 
    
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    
    i+=1 
    embeds.append(discord.Embed(color=self.bot.color, title=f"{commandname}", description=command.description).set_author(name=self.author.name, icon_url=self.author.display_avatar.url if not None else '')
    
    .add_field(name="aliases", value=', '.join(map(str, command.aliases)) or "none")
    .add_field(name="permissions", value=command.brief or "any")
    .add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False)
    .set_footer(text=f"module: {command.cog_name} ・ page {i}/{len(self.command.commands)}", icon_url=self.author.display_avatar.url if not None else ''))
     
   return await self.pages(embeds)  
    
  async def pages(self, embeds: List[Union[discord.Embed, str]]) -> discord.Message:

        if len(embeds) == 1:
            
            if isinstance(embeds[0], discord.Embed):
                return await self.reply(embed=embeds[0])
            
            elif isinstance(embeds[0], str):
                return await self.reply(embeds[0])

        PreviousButton = discord.ui.Button(style=discord.ButtonStyle.grey, emoji="<:left:1259608758800220251>")
        NextButton = discord.ui.Button(style=discord.ButtonStyle.grey, emoji="<:right:1259608897308721152>")
        DeleteButton = discord.ui.Button(style=discord.ButtonStyle.grey, emoji="<:false:1259606495234887740>")

        await Paginator.Simple(
            PreviousButton=PreviousButton,
            NextButton=NextButton,
            DeleteButton=DeleteButton,
            InitialPage=0,
            timeout=60
        ).start(self, pages=embeds)
        
  async def paginator(self, contents: List[str], title: str = None, author: dict = {'name': '', 'icon_url': None}):

        iterator = [m for m in utils.as_chunks(contents, 10)]
        embeds = [
            Embed(
                color=self.bot.color,
                title=title,
                description='\n'.join([f"`{(m.index(f)+1)+(iterator.index(m)*10)}.` {f}" for f in m])
            ).set_author(**author)
            for m in iterator
        ]
        return await self.pages(embeds)

  async def reply(self, content: Optional[str] = None, *, embed: Optional[discord.Embed] = None, view: Optional[View] = None, mention_author: Optional[bool] = False, file: Optional[discord.File] = discord.utils.MISSING,
        files: Optional[Sequence[discord.File]] = discord.utils.MISSING) -> discord.Message:
   
   reskin = await self.bot.db.fetchrow("SELECT * FROM reskin WHERE user_id = $1 AND toggled = $2", self.author.id, True)
   if reskin != None and reskin['toggled']:
     
     hook = await self.webhook(self.message.channel)
     
     if view == None: return await hook.send(content=content, embed=embed, username=reskin['name'], avatar_url=reskin['avatar'], file=file)
     
     return await hook.send(content=content, embed=embed, username=reskin['name'], avatar_url=reskin['avatar'], view=view, file=file)
   return await self.send(content=content, embed=embed, reference=self.message, view=view, mention_author=mention_author, file=file)
 
  async def send(self, content: Optional[str] = None, *, embed: Optional[discord.Embed] = None, view: Optional[View] = discord.utils.MISSING, mention_author: Optional[bool] = False, allowed_mentions: discord.AllowedMentions = discord.utils.MISSING,  reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]] = None, file: Optional[discord.File] = discord.utils.MISSING,
        files: Optional[Sequence[discord.File]] = discord.utils.MISSING) -> discord.Message:
   
   reskin = await self.bot.db.fetchrow("SELECT * FROM reskin WHERE user_id = $1 AND toggled = $2", self.author.id, True)
   if reskin != None and reskin['toggled']:
     
     hook = await self.webhook(self.message.channel)
     return await hook.send(content=content, embed=embed, username=reskin['name'], avatar_url=reskin['avatar'], view=view, allowed_mentions=allowed_mentions, file=file)
   
   return await self.channel.send(content=content, embed=embed, view=view, allowed_mentions=allowed_mentions, reference=reference, mention_author=mention_author, file=file)
  
  async def webhook(self, channel) -> discord.Webhook:
   
   for webhook in await channel.webhooks():
     
     if webhook.user == self.me:
       return webhook
   
   return await channel.create_webhook(name='evict')

  async def cmdhelp(self): 
    
    command = self.command
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    
    embed = discord.Embed(color=self.bot.color, title=commandname, description=command.description)
    embed.set_author(name=self.author.name, icon_url=self.author.display_avatar.url if not None else '')
    embed.add_field(name="aliases", value=', '.join(map(str, command.aliases)) or "none")
    embed.add_field(name="permissions", value=command.brief or "any")
    embed.add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False)
    embed.set_footer(text=f'module: {command.cog_name}', icon_url=self.author.display_avatar.url if not None else '')
    
    await self.reply(embed=embed)
    
class HelpCommand(commands.HelpCommand):
  def __init__(self, **kwargs):
   self.ec_color = 0xCCCCFF
   super().__init__(**kwargs)

  async def send_bot_help(self, ctx: commands.Context) -> None:
    return await self.context.reply(f'{self.context.author.mention}: check <https://evict.cc/commands> for list of commands')
  
  async def send_command_help(self, command: commands.Command):
    
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    
    embed = discord.Embed(color=self.ec_color, title=commandname, description=command.description)
    embed.set_author(name=self.context.author.name, icon_url=self.context.author.display_avatar.url if not None else '')
    embed.add_field(name="aliases", value=', '.join(map(str, command.aliases)) or "none")
    embed.add_field(name="permissions", value=command.brief or "any")
    embed.add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False)
    embed.set_footer(text=f'module: {command.cog_name}', icon_url=self.context.author.display_avatar.url if not None else '')
    
    await self.context.reply(embed=embed)

  async def send_group_help(self, group: commands.Group): 
   
   ctx = self.context
   embeds = []
   i=0
   
   for command in group.commands: 
    commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
    i+=1 
    embeds.append(discord.Embed(color=self.ec_color, title=f"{commandname}", description=command.description).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url if not None else '').add_field(name="usage", value=f"```{commandname} {command.usage if command.usage else ''}```", inline=False).set_footer(text=f"module: {command.cog_name} • aliases: {', '.join(a for a in command.aliases) if len(command.aliases) > 0 else 'none'} ・ {i}/{len(group.commands)}"))
     
   return await ctx.pages(embeds) 