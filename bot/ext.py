from discord.ext import commands
import discord, datetime, time
from typing import Union
from math import log, floor


class Client(object): 
  def __init__(self, bot: commands.Bot): 
    self.bot = bot 
    
  async def success(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.user.mention}: {message}"), ephemeral=ephemeral)
  
  async def error(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.error_color, description=f"{self.bot.no} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.user.mention}: {message}"), ephemeral=ephemeral)
  
  async def warning(self, ctx: Union[commands.Context, discord.Interaction], message: str, ephemeral: bool=True) -> discord.Message: 
   if isinstance(ctx, commands.Context): return await ctx.reply(embed=discord.Embed(color=self.bot.error_color, description=f"{self.bot.warning} {ctx.author.mention}: {message}"))
   else: return await ctx.response.send_message(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.user.mention}: {message}"), ephemeral=ephemeral)

  def is_dangerous(self, role: discord.Role) -> bool:
     permissions = role.permissions
     return any([
      permissions.kick_members, permissions.ban_members,
      permissions.administrator, permissions.manage_channels,
      permissions.manage_guild, permissions.manage_messages,
      permissions.manage_roles, permissions.manage_webhooks,
      permissions.manage_emojis_and_stickers, permissions.manage_threads,
      permissions.mention_everyone, permissions.moderate_members])
     
  def human_format(self, number) -> str:
    units = ['', 'K', 'M', 'G', 'T', 'P']
    if number < 1000:
      return number

    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])
  
  def relative_time(self, date):
    """Take a datetime and return its "age" as a string.
    The age can be in second, minute, hour, day, month or year. Only the
    biggest unit is considered, e.g. if it's 2 days and 3 hours, "2 days" will
    be returned.
    Make sure date is not in the future, or else it won't work.
    """

    def formatn(n, s):
        """Add "s" if it's plural"""

        if n == 1:
            return "1 %s" % s
        elif n > 1:
            return "%d %ss" % (n, s)

    def qnr(a, b):
        """Return quotient and remaining"""

        return a / b, a % b

    class FormatDelta:

        def __init__(self, dt):
            now = datetime.datetime.now()
            delta = now - dt
            self.day = delta.days
            self.second = delta.seconds
            self.year, self.day = qnr(self.day, 365)
            self.month, self.day = qnr(self.day, 30)
            self.hour, self.second = qnr(self.second, 3600)
            self.minute, self.second = qnr(self.second, 60)

        def format(self):
            for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                n = getattr(self, period)
                if n >= 1:
                    return '{0} ago'.format(formatn(n, period))
            return "just now"

    return FormatDelta(date).format()
    
  @property 
  def uptime(self) -> str:
    uptime = int(time.time() - self.bot.uptime)
    seconds_to_minute   = 60
    seconds_to_hour     = 60 * seconds_to_minute
    seconds_to_day      = 24 * seconds_to_hour

    days    =   uptime // seconds_to_day
    uptime    %=  seconds_to_day

    hours   =   uptime // seconds_to_hour
    uptime    %=  seconds_to_hour

    minutes =   uptime // seconds_to_minute
    uptime    %=  seconds_to_minute

    seconds = uptime
    if days > 0: return ("{} days, {} hours, {} minutes, {} seconds".format(days, hours, minutes, seconds))
    if hours > 0 and days == 0: return ("{} hours, {} minutes, {} seconds".format(hours, minutes, seconds))
    if minutes > 0 and hours == 0 and days == 0: return ("{} minutes, {} seconds".format(minutes, seconds))
    if minutes == 0 and hours == 0 and days == 0: return ("{} seconds".format(seconds))  

  @property
  def ping(self) -> int: 
    return round(self.bot.latency * 1000)
  
  def is_dangerous(self, role: discord.Role) -> bool:
     permissions = role.permissions
     return any([
      permissions.kick_members, permissions.ban_members,
      permissions.administrator, permissions.manage_channels,
      permissions.manage_guild, permissions.manage_messages,
      permissions.manage_roles, permissions.manage_webhooks,
      permissions.manage_emojis_and_stickers, permissions.manage_threads,
      permissions.mention_everyone, permissions.moderate_members])
  
  def ordinal(self, num: int) -> str:
     """Convert from number to ordinal (10 - 10th)""" 
     numb = str(num) 
     if numb.startswith("0"): numb = numb.strip('0')
     if numb in ["11", "12", "13"]: return numb + "th"
     if numb.endswith("1"): return numb + "st"
     elif numb.endswith("2"):  return numb + "nd"
     elif numb.endswith("3"): return numb + "rd"
     else: return numb + "th"