import datetime, discord, emoji, re
from discord.ext import commands

class TimeConverter(object): 
    def convert_datetime(self, date: datetime.datetime=None):
     if date is None: return None  
     month = f'0{date.month}' if date.month < 10 else date.month 
     day = f'0{date.day}' if date.day < 10 else date.day 
     year = date.year 
     minute = f'0{date.minute}' if date.minute < 10 else date.minute 
     if date.hour < 10: 
      hour = f'0{date.hour}'
      meridian = "AM"
     elif date.hour > 12: 
      hour = f'0{date.hour - 12}' if date.hour - 12 < 10 else f"{date.hour - 12}"
      meridian = "PM"
     else: 
      hour = date.hour
      meridian = "PM"  
     return f"{month}/{day}/{year} at {hour}:{minute} {meridian} ({discord.utils.format_dt(date, style='R')})" 

    def ordinal(self, num: int) -> str:
     """Convert from number to ordinal (10 - 10th)""" 
     numb = str(num) 
     if numb.startswith("0"): numb = numb.strip('0')
     if numb in ["11", "12", "13"]: return numb + "th"
     if numb.endswith("1"): return numb + "st"
     elif numb.endswith("2"):  return numb + "nd"
     elif numb.endswith("3"): return numb + "rd"
     else: return numb + "th" 
     
class Modals: 
   class Name(discord.ui.Modal, title="change the role name"):
      name = discord.ui.TextInput(
        label='role name',
        placeholder='your new role name here',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.send_warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         await role.edit(name=self.name.value)
         return await interaction.client.ext.send_success(interaction, "Changed the **booster role** name in **{}**".format(self.name.value), ephemeral=True)

   class Icon(discord.ui.Modal, title="change the role icon"):
      name = discord.ui.TextInput(
        label='role icon',
        placeholder='this should be an emoji',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
       try: 
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.send_warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         icon = ""
         if emoji.is_emoji(self.name.value): icon = self.name.value 
         else:
          emojis = re.findall(r'<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>', self.name.value)
          emoj = emojis[0]
          format = ".gif" if emoj[0] == "a" else ".png"
          url = "https://cdn.discordapp.com/emojis/{}{}".format(emoj[2], format)
          icon = await interaction.client.session.read(url)
         await role.edit(display_icon=icon) 
         return await interaction.client.ext.send_success(interaction, "Changed the **booster role** icon", ephemeral=True)  
       except: return await interaction.client.ext.send_error(interaction, "Unable to change the role icon", ephemeral=True)

   class Color(discord.ui.Modal, title="change the role colors"):
      name = discord.ui.TextInput(
        label='role color',
        placeholder='this should be a hex code',
        style=discord.TextStyle.short,
        required=True
    )

      async def on_submit(self, interaction: discord.Interaction):
       try: 
         check = await interaction.client.db.fetchrow("SELECT * FROM booster_roles WHERE guild_id = {} AND user_id = {}".format(interaction.guild.id, interaction.user.id))         
         if check is None: return await interaction.client.ext.send_warning(interaction, "You don't have a booster role. Please use `boosterrole create` command first", ephemeral=True)
         role = interaction.guild.get_role(check['role_id'])
         color = self.name.value.replace("#", "")
         color = int(color, 16)
         await role.edit(color=color)
         return await interaction.client.ext.send_success(interaction, "Changed the **booster role** color", ephemeral=True)
       except: return await interaction.client.ext.send_error(interaction, "Unable to change the role color", ephemeral=True)
       
class Messages: 

  def good_message(message: discord.Message) -> bool: 
   if not message.guild or message.author.bot or message.content == "": return False 
   return True

class OwnerConfig:
    async def send_dm(ctx: commands.Context, member: discord.Member, action: str, reason: str): 
        embed = discord.Embed(color=ctx.bot.color, description=f"You have been **{action}** in every server resent is in.\n{f'**Reason:** {reason}' if reason != 'No reason provided' else ''}")
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"sent from {ctx.author}", disabled=True))
        try: await member.send(embed=embed, view=view)
        except: pass
        
class Time:
    def format_duration(self, timestamp):
        duration = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
        years = duration.days // 365
        months = duration.days % 365 // 30
        days = duration.days % 30
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if years > 0:
            parts.append(f"{years} {'year' if years == 1 else 'years'}")
        if months > 0:
            parts.append(f"{months} {'month' if months == 1 else 'months'}")
        if days > 0:
            parts.append(f"{days} {'day' if days == 1 else 'days'}")
        if hours > 0:
            parts.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
        if minutes > 0:
            parts.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
        if seconds > 0:
            parts.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")

        return ", ".join(parts)