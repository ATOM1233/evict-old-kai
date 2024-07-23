from discord import ButtonStyle, Embed, Interaction, Message, HTTPException
from discord.ext.commands import Context as DefaultContext
from discord.ui import Button, View, Modal, TextInput
from asyncio import TimeoutError
from contextlib import suppress
from typing import Union
from discord.ext import commands
import discord

class CustomInteraction:
    def __init__(self, interaction: Interaction):
        self.interaction = interaction
    async def interection_error(self, message: str, ephemeral: bool = True) -> None:  # Changed default to True
        await self.interaction.response.send_message(
            embed=Embed(color=self.bot.color, description=f"{self.interaction.user.mention}: {message}"), 
            ephemeral=ephemeral
        )
    async def interaction_warn(self, message: str, ephemeral: bool = True) -> None:  # Changed default to True
        await self.interaction.response.send_message(
            embed=Embed(color=self.bot.color, description=f"{self.interaction.user.mention}: {message}"), 
            ephemeral=ephemeral
        )
    async def interaction_approve(self, message: str, ephemeral: bool = True) -> None:  # Changed default to True
        await self.interaction.response.send_message(
            embed=Embed(color=self.bot.color, description=f"{self.interaction.user.mention}: {message}"), 
            ephemeral=ephemeral
        )

class emoji:
    next = "<:right:1263727130370637995>"
    previous = "<:left:1263727060078035066>"
    cancel = "<:deny:1263727013433184347>"
    navigate = "<:navigate2:1242676587862822985>"


class EmbedBuilder:
    def ordinal(self, num: int) -> str:
        """Convert from number to ordinal (10 - 10th)"""
        numb = str(num).lstrip('0')
        if numb in ["11", "12", "13"]:
            return numb + "th"
        return numb + {"1": "st", "2": "nd", "3": "rd"}.get(numb[-1], "th")


class GoToModal(Modal, title="Change the Page"):
    page = TextInput(label="Page", placeholder="Enter page number", max_length=3)

    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds

    async def on_submit(self, interaction: Interaction) -> None:
        custom_interaction = CustomInteraction(interaction)
        try:
            page_number = int(self.page.value)
            if not (1 <= page_number <= len(self.embeds)):
                await custom_interaction.warn(f"You can only select a page **between** 1 and {len(self.embeds)}", ephemeral=True)
            else:
                page = self.embeds[page_number - 1]
                if isinstance(page, Embed):
                    await interaction.response.edit_message(embed=page)
                else:
                    await interaction.response.edit_message(content=page)
        except ValueError:
            await custom_interaction.warn("Please enter a valid page number.", ephemeral=True)
        except Exception as e:
            await custom_interaction.warn(f"An error occurred: {e}", ephemeral=True)

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await CustomInteraction(interaction).warn(f"Unable to change the page: {error}", ephemeral=True)

class PaginatorButton(Button):
    def __init__(self, emoji: str, style: ButtonStyle, paginator: 'Paginator'):
        super().__init__(emoji=emoji, style=style, custom_id=emoji)
        self.paginator = paginator

    async def callback(self, interaction: Interaction) -> None:
        try:
            if self.custom_id == emoji.navigate:
                modal = GoToModal(self.paginator.pages)
                await interaction.response.send_modal(modal)
                await modal.wait()
                try:
                    self.paginator.current_page = int(modal.page.value) - 1
                except ValueError:
                    return
            else:
                await interaction.response.defer()
                if self.custom_id == emoji.previous:
                    self.paginator.current_page = (self.paginator.current_page - 1) % len(self.paginator.pages)
                elif self.custom_id == emoji.next:
                    self.paginator.current_page = (self.paginator.current_page + 1) % len(self.paginator.pages)
                elif self.custom_id == emoji.cancel:
                    with suppress(HTTPException):
                        await self.paginator.message.delete()
                    return

            page = self.paginator.pages[self.paginator.current_page]
            await self.paginator.message.edit(embed=page if isinstance(page, Embed) else None, content=page if not isinstance(page, Embed) else None, view=self.paginator)
        except Exception as e:
            await CustomInteraction(interaction).warn(f"An error occurred: {e}", ephemeral=True)

class Paginator(View):
    def __init__(self, ctx: DefaultContext, pages: list[Union[Embed, str]]) -> None:
        super().__init__(timeout=30)
        self.ctx = ctx
        self.pages = pages
        self.current_page = 0
        self.message = None
        self.add_initial_buttons()
        self.color = self.bot.color

    def add_initial_buttons(self):
        self.add_item(PaginatorButton(emoji=emoji.previous, style=ButtonStyle.blurple, paginator=self))
        self.add_item(PaginatorButton(emoji=emoji.next, style=ButtonStyle.blurple, paginator=self))
        self.add_item(PaginatorButton(emoji=emoji.navigate, style=ButtonStyle.grey, paginator=self))
        self.add_item(PaginatorButton(emoji=emoji.cancel, style=ButtonStyle.red, paginator=self))

    @property
    def type(self) -> str:
        return "embed" if isinstance(self.pages[0], Embed) else "text"

    async def send(self, content: Union[Embed, str], **kwargs) -> Message:
        if isinstance(content, Embed):
            return await self.ctx.reply(embed=content, **kwargs)
        else:
            return await self.ctx.reply(content=content, **kwargs)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await CustomInteraction(interaction).error("You are not authorized to use this **Interaction**.")
            return False
        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass
            except Exception as e:
                import logging
                logging.error(f"An error occurred in Paginator.on_timeout: {e}")

    async def start(self) -> Message:
        self.message = await self.send(self.pages[0] if len(self.pages) == 1 else self.pages[self.current_page], view=self if len(self.pages) > 1 else None)

    async def start(self) -> Message:
        self.message = await self.send(self.pages[0] if len(self.pages) == 1 else self.pages[self.current_page], view=self if len(self.pages) > 1 else None)