import discord, asyncpg, typing, time, os

from typing import List
from humanfriendly import format_timespan

from discord.ext import commands
from discord.gateway import DiscordWebSocket

from bot.utils import StartUp
from bot.helpers import EvictContext, HelpCommand
from bot.ext import Client
from bot.database import create_db
from bot.headers import Session
from bot.dynamicrolebutton import DynamicRoleButton

from cogs.voicemaster import vmbuttons
from cogs.ticket import CreateTicket, DeleteTicket
from cogs.giveaway import GiveawayView

from rivalapi.rivalapi import RivalAPI

DiscordWebSocket.identify = StartUp.identify

class Evict(commands.Bot):
  def __init__(self, db: asyncpg.Pool=None):
        super().__init__(command_prefix=EvictContext.getprefix, allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True, replied_user=False), intents=discord.Intents.all(), 
                         owner_ids=[214753146512080907, 598125772754124823],
                         help_command=HelpCommand(), strip_after_prefix=True, activity=discord.CustomActivity(name="🔗 evict.cc"))
        
        self.db = db
        
        self.color = 0xCCCCFF
        self.error_color= 0xFFFFED
        self.yes = "<:approved:1259606226535317615>"
        self.no = "<:false:1259606495234887740>"
        self.warning = "<:warning:1259608056832987248>"
        self.left = "<:left:1259608758800220251>"
        self.right = "<:right:1259608897308721152>"
        self.goto = "<:filter:1259609300221821039>"
        
        self.ext = Client(self)
        
        self.m_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.member)
        self.c_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.channel)
        self.m_cd2=commands.CooldownMapping.from_cooldown(1,10,commands.BucketType.member)
        self.global_cd = commands.CooldownMapping.from_cooldown(2, 3, commands.BucketType.member)
        
        self.uptime = time.time()
        self.session = Session()
        
        self.evict_api = os.environ.get("evict_api")
        self.rival_api = os.environ.get("rival_api")
        self.proxy_url = os.environ.get("proxy_url")
        self.rival = RivalAPI(self.rival_api)
        
        self.commands_url = os.environ.get("commands_url")
        self.support_server = os.environ.get("support_server")
        
  async def create_db_pool(self):
        self.db = await asyncpg.create_pool(port="5432", database="evict", user="postgres", host="localhost", password="admin")
      
  async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
      if isinstance(error, commands.CommandNotFound): return 
      if isinstance(error, commands.NotOwner): pass
      if isinstance(error, commands.CheckFailure): 
        if isinstance(error, commands.MissingPermissions): return await ctx.warning(f"This command requires **{error.missing_permissions[0]}** permission")
      elif isinstance(error, commands.CommandOnCooldown):
        if ctx.command.name != "hit": return await ctx.reply(embed=discord.Embed(color=0xE1C16E, description=f"⌛ {ctx.author.mention}: You are on cooldown. Try again in {format_timespan(error.retry_after)}"), mention_author=False)    
      if isinstance(error, commands.MissingRequiredArgument): return await ctx.cmdhelp()
      if isinstance(error, commands.EmojiNotFound): return await ctx.warning(f"Unable to convert {error.argument} into an **emoji**")
      if isinstance(error, commands.MemberNotFound): return await ctx.warning(f"Unable to find member **{error.argument}**")
      if isinstance(error, commands.UserNotFound): return await ctx.warning(f"Unable to find user **{error.argument}**")
      if isinstance(error, commands.RoleNotFound): return await ctx.warning(f"Couldn't find role **{error.argument}**")
      if isinstance(error, commands.ChannelNotFound): return await ctx.warning(f"Couldn't find channel **{error.argument}**")
      if isinstance(error, commands.ThreadNotFound): return await ctx.warning(f"I was unable to find the thread **{error.argument}**")
      if isinstance(error, commands.UserConverter): return await ctx.warning(f"Couldn't convert that into an **user** ")
      if isinstance(error, commands.MemberConverter): return await ctx.warning("Couldn't convert that into a **member**")
      if isinstance(error, commands.BadArgument): return await ctx.warning(error.args[0])
      if isinstance(error, commands.BotMissingPermissions): return await ctx.warning(f"I do not have enough **permissions** to execute this command")
      if isinstance(error, commands.CommandInvokeError): return await ctx.warning(error.original)
      if isinstance(error, discord.HTTPException): return await ctx.warning("Unable to execute this command")
      if isinstance(error, commands.NoPrivateMessage): return await ctx.warning(f"This command cannot be used in private messages.")
      if isinstance(error, commands.UserInputError): return await ctx.send_help(ctx.command.qualified_name)
      if isinstance(error, discord.NotFound): return await ctx.warning(f"**Not found** - the **ID** is invalid")
      if isinstance(error, commands.MemberNotFound): return await ctx.warning(f"I was unable to find a member with the name: **{error.argument}**")
      if isinstance(error, commands.GuildNotFound): return await ctx.warning(f"I was unable to find that **server** or the **ID** is invalid")
      if isinstance(error, commands.BadInviteArgument): return await ctx.warning(f"Invalid **invite code** given")
        
  async def channel_ratelimit(self,message:discord.Message) -> typing.Optional[int]:
      cd=self.c_cd
      bucket=cd.get_bucket(message)
      return bucket.update_rate_limit()

  async def on_message_edit(self, before, after):
        if before.content != after.content: await self.process_commands(after)

  async def prefixes(self, message: discord.Message) -> List[str]: 
     prefixes = []
     for l in set(p for p in await self.command_prefix(self, message)): prefixes.append(l)
     return prefixes

  async def member_ratelimit(self,message:discord.Message) -> typing.Optional[int]:
        cd=self.m_cd
        bucket=cd.get_bucket(message)
        return bucket.update_rate_limit()
      
  async def on_message(self, message: discord.Message): 
      
        channel_rl=await self.channel_ratelimit(message)
        member_rl=await self.member_ratelimit(message)
      
        if channel_rl == True:
          return
      
        if member_rl == True:
          return
      
        if message.content == "<@{}>".format(self.user.id): return await message.reply(content="prefixes: " + " ".join(f"`{g}`" for g in await self.prefixes(message)))
        await self.process_commands(message) 
    
  async def setup_hook(self):
        self.add_view(vmbuttons())
        self.add_dynamic_items(DynamicRoleButton)
        self.add_view(CreateTicket())
        self.add_view(DeleteTicket())
        self.add_view(GiveawayView())
        await self.load_extension('jishaku')
        await StartUp.loadcogs(self)
        await self.create_db_pool()
        await create_db(self)

  async def get_context(self, message: discord.Message, cls=EvictContext) -> EvictContext:
      return await super().get_context(message, cls=cls)