import discord, asyncpg, typing
from discord.ext import commands
from bot.utils import StartUp
from bot.helpers import EvictContext, HelpCommand
from bot.ext import Client
from bot.database import create_db
from rivalapi.rivalapi import RivalAPI
from humanfriendly import format_timespan

class Evict(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="+",allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True, replied_user=False), intents=discord.Intents.all(), 
                         owner_ids=[214753146512080907, 598125772754124823],
                         help_command=HelpCommand())
        
        self.color = 0xffffff
        self.yes = "<:approved:1209081187679862784>"
        self.no = "<:false:1209081189269512253>"
        self.warning = "<:warning:1209081190418743326>"
        self.left = "<:left:1227724412967714907>"
        self.right = "<:right:1227724250165678091>"
        self.goto = "<:filter:1208241278891073547>"
        self.ext = Client(self)
        self.support_server = 'https://discord.gg/evict'
        self.commands_url = 'https://evict.dev/commands'
        self.evict_api = "58ZCTj0fTkai"
        self.rival_api = "88d7eac6-df61-4a08-a95d-8904f81cc099"
        self.rival = RivalAPI(self.rival_api)
        self.m_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.member)
        self.c_cd=commands.CooldownMapping.from_cooldown(1,5,commands.BucketType.channel)
        self.m_cd2=commands.CooldownMapping.from_cooldown(1,10,commands.BucketType.member)
        self.global_cd = commands.CooldownMapping.from_cooldown(2, 3, commands.BucketType.member)
        self.proxy_url = "http://38gt3f7lsejwhm4:5xarwv0int6boz5@rp.proxyscrape.com:6060"
        
    async def create_db_pool(self):
        self.db = await asyncpg.create_pool(port="5432", database="testing", user="postgres", host="localhost", password="admin")
      
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
        print("Attempting To Start")
        await self.load_extension('jishaku')
        await StartUp.loadcogs(self)
        await self.create_db_pool()
        await create_db(self)
        print(f"Connected to Discord API as {self.user}")

    async def get_context(self, message: discord.Message, cls=EvictContext) -> EvictContext:
      return await super().get_context(message, cls=cls)