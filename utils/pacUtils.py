import datetime
import random
import re
from typing import List, Optional
import aiosqlite
import nextcord
from nextcord.ext import menus

from userlevel import userLevel, totalxp
from EmojiCodes import EMOJI_CODES

pacPoints = 0
pacLives = 3

date = datetime.datetime.now()
date.strftime("%x")

class maps():
    class mapOne():
        def pacmanMaps() -> str:
            return (("🟦") * 19 + '\n' +
                    "🟦" + ("⬛" * 4) + "🟦" + ("⬛" * 7) + "🟦" + ("⬛" * 4) + "🟦" + '\n' +
                    "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + "⬛" + ("🟦" * 5) + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + '\n' +
                    "🟦" + ("⬛" * 2) + "🟦" + ("⬛" * 5) + "🟦" + ("⬛" * 5) + "🟦" + ("⬛" * 2) + "🟦" + '\n' +
                    ("🟦" * 2) + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + '\n' +
                    ("⬛" * 5) + "🟦" + "⬛" + "🟦" + ("⬛" * 3) + "🟦" + "⬛" + "🟦" + ("⬛" * 5) + '\n' +
                    ("🟦" * 2) + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 5) + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 2) + '\n' +
                    ("🟦" * 2) + ("⬛" * 3) + "🟦" + ("⬛" * 3) + EMOJI_CODES["pacman"]["ghosts"]["red_ghost"]["up"] + ("⬛" * 3) + "🟦" + ("⬛" * 3) + ("🟦" * 2) + '\n' +
                    ("🟦" * 2) + "⬛" + "🟦" + ("⬛" * 3) + ("🟦" * 2) + "🔳" + ("🟦" * 2) + ("⬛" * 3) + "🟦" + "⬛" + ("🟦" * 2) + '\n' +
                    "🟦" + ("⬛" * 2) + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + EMOJI_CODES["pacman"]["ghosts"]["blue_ghost"]["up"] + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + ("⬛" * 2) + "🟦" + '\n')

        def pacmanMapsPtTwo() -> str:
            return ("🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + "⬛" + "🟦" + EMOJI_CODES["pacman"]["ghosts"]["pink_ghost"]["up"] + "⬛" + EMOJI_CODES["pacman"]["ghosts"]["orange_ghost"]["up"] + "🟦" + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + '\n' +
                    "🟦" + ("⬛" * 4) + "🟦" + "⬛" + ("🟦" * 5) + "⬛" + "🟦" + ("⬛" * 4) + "🟦" + '\n' +
                    "🟦" + ("⬛" * 4) + "🟦"  + ("⬛" * 7) + "🟦" + ("⬛" * 4) + "🟦" + '\n' +
                    ("🟦" * 2) + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 5) + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 2) + '\n' +
                    "🟦" + ("⬛" * 8) + "🟦" + ("⬛" * 8) + "🟦" + '\n' +
                    "🟦" + "⬛" + ("🟦" * 2) + "⬛" + ("🟦" * 3) + "⬛" + "🟦" + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + '\n' +
                    "🟦" + ("⬛" * 2) + "🟦" + "⬛" + "🟦" + ("⬛" * 7) + "🟦" + "⬛" + "🟦" + ("⬛" * 2) + "🟦" + '\n' +
                    ("🟦" * 2) + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + ("🟦" * 5) + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + '\n' +
                    "🟦" + ("⬛" * 4) + "🟦" + ("⬛" * 3) + "🟦" + ("⬛" * 3) + "🟦" + ("⬛" * 4) + "🟦" + '\n' +
                    "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + '\n')

        def pacmanMapsPtThree() -> str:
            return ("🟦" + ("⬛" * 6) + "🟦" + ("⬛" * 3) + "🟦" + ("⬛" * 6) + "🟦" + '\n' +
                    ("🟦" * 19))
    
    class mapTwo():
        def pacmanMaps() -> str:
            return (("🟦" * 19) + '\n' +
                    "🟦" + ("⬛" * 17) + "🟦" + '\n' +
                    "🟦" + "⬛" + ("🟦" * 4) + "⬛" + ("🟦" * 5) + "⬛" + ("🟦" * 4) + "⬛" + "🟦" + '\n' +
                    "🟦" + ("⬛" * 2) + "🟦" + ("⬛" * 5) + "🟦" + ("⬛" * 5) + "🟦" + ("⬛" * 2) + "🟦" + '\n' + 
                    ("🟦" * 2) + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + '\n' +
                    ("⬛" * 5) + "🟦" + "⬛" + "🟦" + ("⬛" * 3) + "🟦" + "⬛" + "🟦" + ("⬛" * 5) + '\n' +
                    ("🟦" * 2) + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 5) + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 2) + '\n' +
                    ("🟦" * 2) + ("⬛" * 7) + EMOJI_CODES["pacman"]["ghosts"]["red_ghost"]["up"] + ("⬛" * 7) + ("🟦" * 2) + '\n' +
                    ("🟦" * 2) + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 2) + "🔳" + ("🟦" * 2) + "⬛" + ("🟦" * 3) + "⬛" + ("🟦" * 2) + '\n' +
                    "🟦" + ("⬛" * 4) + "🟦" + "⬛" + "🟦" + EMOJI_CODES["pacman"]["ghosts"]["pink_ghost"]["up"] + EMOJI_CODES["pacman"]["ghosts"]["blue_ghost"]["up"] + EMOJI_CODES["pacman"]["ghosts"]["orange_ghost"]["up"] + "🟦" + "⬛" + "🟦" + ("⬛" * 4) + "🟦" + '\n')
        def pacmanMapsPtTwo() -> str:
            return ("🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + "⬛" + ("🟦" * 5) + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + '\n' +
                    "🟦" + "⬛" + "🟦" + ("⬛" * 13) + "🟦" + "⬛" + "🟦" + '\n' +
                    "🟦" + "⬛" + "🟦" + "⬛" + ("🟦" * 4) + "⬛" + "🟦" + "⬛" + ("🟦" * 4) + "⬛" + "🟦" + "⬛" + "🟦" + '\n' +
                    ("⬛" * 5) + "🟦" + ("⬛" * 3) + "🟦" + ("⬛" * 3) + "🟦" + ("⬛" * 5) + '\n' +
                    "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + "⬛" + ("🟦" * 5) + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + '\n' +
                    "🟦" + ("⬛" * 17) + "🟦" + '\n' +
                    "🟦" + "⬛" + ("🟦" * 4) + "⬛" + ("🟦" * 5) + "⬛" + ("🟦" * 4) + "⬛" + "🟦" + '\n' +
                    "🟦" + ("⬛" * 4) + "🟦" + "⬛" + "🟦" + ("⬛" * 3) + "🟦" + "⬛" + "🟦" + ("⬛" * 4) + "🟦" + '\n')
        def pacmanMapsPtThree() -> str:
            return ("🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + "🟦" + "⬛" + ("🟦" * 2) + "⬛" + "🟦" + '\n' + 
                    ("🟦" * 19))

    possible_map = [
        mapOne(),
        mapTwo()
    ]
    selectMap = random.choice(possible_map)

def pacmanLevel() -> int:
    pass

def pacEmbed(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title=f"Pacman\nLevel: {pacmanLevel}", timestamp=date)
    embed.description = ('\n'.join([maps.mapTwo.pacmanMaps()]))
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.add_field(name="", value='\n'.join([maps.mapTwo.pacmanMapsPtTwo()]))
    embed.add_field(name="", value='\n'.join([maps.mapTwo.pacmanMapsPtThree()]), inline=False)
    embed.add_field(name="points", value=pacPoints, inline=False)
    embed.add_field(name="lives", value=pacLives, inline=False)
    embed.set_footer(text="coming soon")
    return embed
        
class controls(menus.ButtonMenu): 
    def __init__(self):
        super().__init__(timeout=None)
        self.moveDir = str
    
    @nextcord.ui.button(emoji="⬅️", style=nextcord.ButtonStyle.blurple, custom_id="pacmanButtons:left")
    async def left(self, button: nextcord.Button, interaction: nextcord.Interaction):
        self.moveDir = "left"
        await interaction.response.send_message(self.moveDir)
    @nextcord.ui.button(emoji="⬇️", style=nextcord.ButtonStyle.danger, custom_id="pacmanButtons:down")
    async def down(self, button: nextcord.Button, interaction: nextcord.Interaction):
        self.moveDir = "down"
        await interaction.response.send_message(self.moveDir)
    @nextcord.ui.button(emoji="⬆️", style=nextcord.ButtonStyle.danger, custom_id="pacmanButtons:up")
    async def up(self, button: nextcord.Button, interaction: nextcord.Interaction):
        self.moveDir = "up"
        await interaction.response.send_message(self.moveDir)
    @nextcord.ui.button(emoji="➡️", style=nextcord.ButtonStyle.blurple, custom_id="pacmanButtons:right")
    async def right(self, button: nextcord.Button, interaction: nextcord.Interaction):
        self.moveDir = "right"
        await interaction.response.send_message(self.moveDir)
    async def prompt(self, ctx):
        await menus.Menu.start(self, ctx, wait=False)
        return self.moveDir

async def updatePacmanEmbed(embed: nextcord.Embed, moveDir: str, ctx, interaction: nextcord.Interaction) -> nextcord.Embed:
    moveDir = await controls("").prompt(ctx)
    if moveDir == "left":
        await interaction.response.send_message("no")

def isPacmanDead(embed: nextcord.Embed) -> bool:
    return "\n\n" in embed.description

async def pacman(bot: nextcord.Client, button: nextcord.Button, message: nextcord.Message) -> bool:
    pass