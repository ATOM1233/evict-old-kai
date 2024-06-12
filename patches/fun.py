import random, discord, aiohttp
from typing import List
from discord.ext import commands

class BlackTea: 
    """BlackTea backend variables"""
    MatchStart = {}
    lifes = {}
    
    async def get_string(): 
      lis = await BlackTea.get_words()
      word = random.choice([l for l in lis if len(l) > 3])
      return word[:3]

    async def get_words(): 
      async with aiohttp.ClientSession() as cs: 
       async with cs.get("https://www.mit.edu/~ecprice/wordlist.100000") as r: 
        byte = await r.read()
        data = str(byte, 'utf-8')
        return data.splitlines()  

    
class RockPaperScissors(discord.ui.View): 
  def __init__(self, ctx: commands.Context):
    self.ctx = ctx   
    self.get_emoji = {"rock": "🪨", "paper": "📰", "scissors": "✂️"} 
    self.status = False 
    super().__init__(timeout=10)

  async def action(self, interaction: discord.Interaction, selection: str): 
        if interaction.user.id != self.ctx.author.id: return await interaction.client.ext.send_warning(interaction, "This is not your game", ephemeral=True)
        botselection = random.choice(["rock", "paper, scissors"])

        def getwinner(): 
            if botselection == "rock" and selection == "scissors": return interaction.client.user.id
            elif botselection == "rock" and selection == "paper": return interaction.user.id
            elif botselection == "paper" and selection == "rock": return interaction.client.user.id
            elif botselection == "paper" and selection == "scissors": return interaction.user.id
            elif botselection == "scissors" and selection == "rock": return interaction.user.id 
            elif botselection == "scissors" and selection == "paper": return interaction.client.user.id 
            else: return "tie"           
    
        if getwinner() == "tie": await interaction.response.edit_message(embed=discord.Embed(color=interaction.client.color, title="Tie!", description=f"You both picked {self.get_emoji.get(selection)}"))
        elif getwinner() == interaction.user.id: await interaction.response.edit_message(embed=discord.Embed(color=interaction.client.color, title="You won!", description=f"You picked {self.get_emoji.get(selection)} and the bot picked {self.get_emoji.get(botselection)}")) 
        else: await interaction.response.edit_message(embed=discord.Embed(color=interaction.client.color, title="Bot won!", description=f"You picked {self.get_emoji.get(selection)} and the bot picked {self.get_emoji.get(botselection)}"))
        await self.disable_buttons()
        self.status = True 

  @discord.ui.button(emoji="🪨")
  async def rock(self, interaction: discord.Interaction, button: discord.ui.Button): 
    return await self.action(interaction, "rock")
  
  @discord.ui.button(emoji="📰")
  async def paper(self, interaction: discord.Interaction, button: discord.ui.Button): 
   return await self.action(interaction, "paper")

  @discord.ui.button(emoji="✂️")
  async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button): 
   return await self.action(interaction, "scissors") 
  
  async def on_timeout(self): 
   if self.status == False: await self.disable_buttons() 

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int, player1: discord.Member, player2: discord.Member):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y
        self.player1 = player1
        self.player2 = player2

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            if interaction.user != self.player1: return await interaction.response.send_message("you can't interact with this button", ephemeral=True)
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now **{self.player2.name}**'s turn"
        else:
            if interaction.user != self.player2: return await interaction.response.send_message("you can't interact with this button", ephemeral=True)
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now **{self.player1.name}'s** turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f'**{self.player1.name}** won!'
            elif winner == view.O:
                content = '**{}** won!'.format(self.player2.name)
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, player1: discord.Member, player2: discord.Member):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y, player1, player2))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X
        
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None
    
    async def on_timeout(self) -> None:
      for item in self.children: item.disabled = True 
      await self.message.edit(view=self.view)   

    async def disable_buttons(self): 
        for item in self.children: 
            item.disabled = True 
        await self.message.edit(view=self)   