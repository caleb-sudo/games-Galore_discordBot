import logging
import os
import random
import re
import datetime
import emoji
import config
import asyncio
import nextcord
import numpy as np
import pandas as pd
import json
import urllib
import keyword
import keyboard
import aiosqlite
import sqlite3
import tetris
import spotify as spot
import printToFile

from pynput.keyboard import Key, Listener
from EmojiCodes import EMOJI_CODES
from dotenv import load_dotenv
from typing import List, Optional
from nextcord import File, ButtonStyle
from nextcord.ui import Button, View
from nextcord.ext import menus, commands
from nextcord.abc import GuildChannel
from databases import Database

#imports all the level information
#imports all posible levels and splits them be line
levels = open("txts/levels.txt").read().splitlines()
#imports the xp needed to reach the next level and splits them be line
xp = open("txts/xp.txt").read().splitlines()
#imports the starting xp (which is always 0), for when you reach the next level and splits them by line
startingXP = open("txts/start.txt").read().splitlines()

#imports the words for wordle
#words used in wordle
popular_words = open("txts/main_words.txt").read().splitlines()
#words not used but are still valid in wordle
all_words = set(word.strip() for word in open("txts/words.txt"))

logging.basicConfig(level=logging.INFO)

load_dotenv()

activity = nextcord.Activity(type=nextcord.ActivityType.listening)
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("w?"), activity=activity, intents=intents)
date = datetime.datetime.now()
date.strftime("%x")

extensions = [
    'cogs.events',
    'cogs.botcmd',
    'cogs.dj',
    'cogs.database',
    'cogs.play',
    'cogs.queue'
]
GUILD_IDS = (
    [int(guild_id) for guild_id in os.getenv("GUILD_IDS", "").split(",")]
    if os.getenv("GUILD_IDS", None)
    else nextcord.utils.MISSING
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

#arrow buttons(up, down, left, right) & pause/play buttons

class mainButtons(menus.ButtonMenu):
    def __init__(self):
        super().__init__(timeout=None)
    
    #left
    @nextcord.ui.button(emoji="⬅️", style=nextcord.ButtonStyle.blurple, custom_id="mainButtons:left")
    async def left(self, button: nextcord.Button, interaction: nextcord.Interaction):
        pass
    
    #up
    @nextcord.ui.button(emoji="⬆️", style=nextcord.ButtonStyle.green, custom_id="mainButtons:up")
    async def up(self, button: nextcord.Button, interaction: nextcord.Interaction):
        pass

    #down
    @nextcord.ui.button(emoji="⬇️", style=nextcord.ButtonStyle.primary, custom_id="mainButtons:down")
    async def down(self, button: nextcord.Button, interaction: nextcord.Interaction):
        pass

    #right
    @nextcord.ui.button(emoji="➡️", style=nextcord.ButtonStyle.secondary, custom_id="mainButtons:right")
    async def right(self, button:nextcord.Button, interaction: nextcord.Interaction):
        pass

    #pause/play
    @nextcord.ui.button(emoji="⏯️", style=nextcord.ButtonStyle.success, custom_id="mainButtons:pause_play")
    async def pause_play(self, button: nextcord.Button, interaction: nextcord.Interaction):
        pass

#wordle command
    WordleUserStreak = None

    async def generate_colored_word(guess: str, answer: str) -> str:
        colored_word = [EMOJI_CODES["gray"][letter] for letter in guess]
        guess_letters: List[Optional[str]] = list(guess)
        answer_letters: List[Optional[str]] = list(answer)
        for i in range(len(guess_letters)):
            if guess_letters[i] == answer_letters[i]:
                colored_word[i] = EMOJI_CODES["green"][guess_letters[i]]
                answer_letters[i] = None
                guess_letters[i] = None
        for i in range(len(guess_letters)):
            if guess_letters[i] is not None and guess_letters[i] in answer_letters:
                colored_word[i] = EMOJI_CODES["yellow"][guess_letters[i]]
                answer_letters[answer_letters.index(guess_letters[i])] = None
        return "".join(colored_word)


    async def generate_blanksWordle() -> str:
        return "\N{WHITE MEDIUM SQUARE}" * 5


    async def generate_puzzle_embed(user: nextcord.User, puzzle_id: int) -> nextcord.Embed:
        embed = nextcord.Embed(title="Wordle", timestamp=date)
        embed.description = "\n".join([db.generate_blanksWordle()] * 6)
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        embed.set_footer(
            text=f"ID: {puzzle_id} ︱ To play, use the command /wordle!\n"
            "To guess, reply to this message with a word."
        )
        return embed

    async def update_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
        puzzle_id = int(embed.footer.text.split()[1])
        answer = popular_words[puzzle_id]
        colored_word = db.generate_colored_word(guess, answer)
        empty_slot = db.generate_blanks_tetris()
        embed.description = embed.description.replace(empty_slot, colored_word, 1)
        num_empty_slots = embed.description.count(empty_slot)
        if guess == answer:
            async with aiosqlite.connect('level.db') as db:
                async with db.cursor() as cursor:
                    #when someone gets the answer with 6 trys
                    if num_empty_slots == 0:
                        embed.description += "\n\nThat was close!\nYou have earned 100 xp"
                        UserXp += 100
                    #when someone gets the answer with 5 trys
                    if num_empty_slots == 1:
                        embed.description += "\n\nGreat!\nYou have earned 200 xp"
                        UserXp += 200
                    #when someone gets the answer with 4 trys
                    if num_empty_slots == 2:
                        embed.description += "\n\nSplendid!\nYou have earned 300 xp"
                        UserXp += 300
                    #when someone gets the answer with 3 trys
                    if num_empty_slots == 3:
                        embed.description += "\n\nWOW!\nYou have earned 400 xp"
                        UserXp += 400
                    #when someone gets the answer with 2 trys
                    if num_empty_slots == 4:
                        embed.description += "\n\nYour a Genius!\nYou have earned 500 xp"
                        UserXp += 500
                    #when someone gets the answer with 1 try
                    if num_empty_slots == 5:
                        embed.description += "\n\nImpossible!\nYou have earned 600 xp"
                        UserXp += 600
                    db.commit()
        #when someone does not get the answer in 6 trys
        elif num_empty_slots == 0:
            embed.description += f"\n\nThe answer was {answer}!\nYou have lost 300 xp"
            UserXp -= 300
        return embed


    def is_valid_word(word: str) -> bool:
        return word in all_words


    def random_puzzle_id() -> int:
        return random.randint(0, len(popular_words) - 1)


    def is_game_over_wordle(embed: nextcord.Embed) -> bool:
        return "\n\n" in embed.description

    async def processMessageAsGuessWordle(bot: nextcord.Client, message: nextcord.Message) -> bool:
        ref = message.reference
        if not ref or not isinstance(ref.resolved, nextcord.Message):
            return False
        parent = ref.resolved

        if parent.author.id != bot.user.id:
            return False

        if not parent.embeds:
            return False

        embed = parent.embeds[0]

        guess = message.content.lower()

        if (
            embed.author.name != message.author.name
            or embed.author.icon_url != message.author.display_avatar.url
        ):
            reply = "Start a new game with /wordle"
            if embed.author:
                reply = f"This game was started by {embed.author.name}. " + reply
            await message.reply(reply, delete_after=10)
            try:
                await message.delete(delay=10)
            except Exception:
                pass
            return True

        if db.is_game_over_wordle(embed):
            await message.reply("The game is already over. Start a new game with /wordle", delete_after=5)
            try:
                await message.delete(delay=5)
            except Exception:
                pass
            return True

        guess = re.sub(r"<@!?\d+>", "", guess).strip()

        bot_name = message.guild.me.nick if message.guild and message.guild.me.nick else bot.user.name

        if len(guess) == 0:
            await message.reply(
                "I am unable to see what you are trying to guess.\n"
                "Please try mentioning me in your reply before the word you want to guess.\n\n"
                f"**For example:**\n{bot.user.mention} crate\n\n"
                f"To bypass this restriction, you can start a game with `@\u200b{bot_name} play` instead of `/wordle`",
                delete_after=14,
            )
            try:
                await message.delete(delay=20)
            except Exception:
                pass
            return True

        if len(guess.split()) > 1:
            await message.reply("Please respond with a single 5-letter word.", delete_after=10)
            try:
                await message.delete(delay=10)
            except Exception:
                pass
            return True

        if not db.is_valid_word(guess):
            await message.reply("That is not a valid word", delete_after=10)
            try:
                await message.delete(delay=10)
            except Exception:
                pass
            return True

        embed = db.update_embed(embed, guess)
        await parent.edit(embed=embed)

        try:
            await message.delete()
        except Exception:
            pass

        return True

    @bot.slash_command(name="wordle", description="Play a game of Wordle\nright now it is being used as db testing", guild_ids=GUILD_IDS)
    async def wordle(interaction: nextcord.Interaction):
        async with aiosqlite.connect("level.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user.name} (userName VARCHAR(255), userID INTEGER, guildName VARCHAR(255), guildID INTEGER, userLevel INTERGER, currentXpToNextLevel INTEGER, TotalXP INTEGER)")
            await db.commit()
        async with aiosqlite.connect("level.db") as dbase:
            async with dbase.cursor() as cursor:
                query = f'INSERT INTO {interaction.user.name} VALUES (?, ?, ?, ?, ?, ?, ?)'
                await cursor.execute(query, (interaction.user.name, interaction.user.id, interaction.guild.name, interaction.guild_id, levels, startingXP, xp))
                select = await cursor.execute('SELECT * FROM level')
                fetch = await select.fetchall()
            await dbase.commit()
        await interaction.response.send_message(f"succsesful\n{fetch}")

    @bot.event
    async def on_message(message: nextcord.Message):
        processed_as_guess = await db.processMessageAsGuessWordle(bot, message)
        if not processed_as_guess:
            await bot.process_commands(message)


#tetris command

tetrisGameover = True
tetris_score = 0
numOfCols = 10
numOfRows = 24
TetrisHorizontalMov = 0
TetrisVerticalMov = -1
TetrisRotateCurrentBlock = False
TetrisDown = False
tetrisPaused = True
TetrisUserHighscore = 0

def empty():
    global empty_block
    empty_block = "\N{BLACK LARGE SQUARE}"
    return empty_block

class blocks():
    def O_block():
        obj = '\n' + "🟨" * 2
        return obj * 2
    def I_block():
        obj = '\n' + "🟦"
        return obj * 4
    def L_block():
        layer1 = '\n' + "🟩" * 3
        layer2 = '\n' + "🟩"
        return layer1 + layer2
    def J_block():
        layer1 = '\n' + "🟪" * 3
        layer2 = '\n' + f"{empty() * 2}🟪"
        return layer1 + layer2
    def T_block():
        layer1 = '\n' + "🟧" * 3
        layer2 = '\n' + f"{empty()}🟧{empty()}"
        return layer1 + layer2
    def Z_block():
        layer1 = '\n' + "🟫" * 2
        layer2 = '\n' + f"{empty()}" + "🟫" * 2
        return layer1 + layer2
    def S_block():
        layer1 = '\n' + f"{empty()}" + "🟥" * 2
        layer2 = '\n' + "🟥" * 2
        return layer1 + layer2


possible_blocks = [
    blocks.O_block(),
    blocks.I_block(),
    blocks.L_block(),
    blocks.J_block(),
    blocks.T_block(),
    blocks.Z_block(),
    blocks.S_block()
]

class tetrisButtons(menus.ButtonMenu):
    def __init__(self):
        super().__init__(timeout=None)
        self.move = None
        self.paused = True

    @nextcord.ui.button(emoji="⬅️", style=nextcord.ButtonStyle.blurple, custom_id="tetrisButtons:left")
    async def left(self):
        self.move = 'left'

    @nextcord.ui.button(emoji="⬇️", style=nextcord.ButtonStyle.danger, custom_id="tetrisButtons:down")
    async def down(self):
        self.move = 'down'

    @nextcord.ui.button(emoji="➡️", style=nextcord.ButtonStyle.blurple, custom_id="tetrisButtons:right")
    async def right(self):
        self.move = 'right'

    @nextcord.ui.button(emoji="⏯️", style=nextcord.ButtonStyle.primary, custom_id="tetrisButtons:pause/play")
    async def pause_play(self):
        if self.paused == True:
            self.paused = False
        else:
            self.paused = True

    async def TetrisPrompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.move, self.paused 

def generate_blocks_tetris() -> str:
    pass

def generate_blanks_tetris() -> str:
    return empty_block * 10

def Tetris_score() -> str:
    pass

def next_block():
    tetris_next = random.choice(possible_blocks)
    return tetris_next

def currentBlock():
    tetris_current = random.choices(possible_blocks)
    return tetris_current

def rotateBlockTetris(self):
    if TetrisRotateCurrentBlock:
        pass

def moveBlockTetris():
    if TetrisDown:
        pass
    elif TetrisDown:
        pass

def TetrisStart():
    pass

def TetrisPause():
    pass

def generate_map_tetris(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Tetris", timestamp=date)
    embed.description = (("\n".join([generate_blanks_tetris()] * 24)))
    embed.add_field(name="Current Score:", value=TetrisHorizontalMov)
    embed.add_field(name="Next Block:", value=next_block())
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(text="\nto play us the buttons at the bottom, Or\nUse the arrow keys on your keyboard(if it works)")
    return embed



async def GameOverTetris(interaction: nextcord.Interaction, user: nextcord.User, message: nextcord.Message) -> bool:
    await message.reply(f"{user.name} {user.display_avatar.url}\nGreat Job {user.name} you have {tetris_score}!\nYour Highscord is {TetrisUserHighscore}")

def TetrisPlay(bot: nextcord.Client, message: nextcord.Message) -> bool:
    ref = message.reference
    if not ref or not isinstance(ref.resolved, nextcord.Message):
        return False
    parent = ref.resolved

    if parent.author.id != bot.user.id:
        return False

    if not parent.embeds:
        return False
    
    embed = parent.embeds[0]
    if (
        embed.author.name != message.author.name
        or embed.author.icon_url != message.author.display_avatar.url
    ):
        reply = "Start a new game with /tetris"
        if embed.author:
            reply = f"This game was started by {embed.author.name}. " + reply

@bot.slash_command(name="tetris", description="play a game of tetris(coming soon)", guild_ids=GUILD_IDS)
async def tetris(interaction: nextcord.Interaction):
    embed = generate_map_tetris(interaction.user)
    await interaction.send(embed=embed, view=tetrisButtons())


#nerdle command

def nerdleboard(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Nerdle", timestamp=date)
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(text="coming soon")
    return embed

@bot.slash_command(name="nerdle", description="play a game of nerdle, which it just like wordle\n but with math (coming soon)", guild_ids=GUILD_IDS)
async def nerdle(interaction: nextcord.Interaction):
    embed = nerdleboard(interaction.user)
    await interaction.send(embed=embed)


#2048 command

two048Points = 0
User2048Highscore = None

#2048 grid sizes selection menu

def random2048startingBlocks():
    possible2048startingBlocks = [
        EMOJI_CODES['2048']['2'],
        EMOJI_CODES['2048']['4']
    ]
    starting2048blocks = random.choices(possible2048startingBlocks)
    return starting2048blocks

async def fourEmbed(user: nextcord.User) -> nextcord.Embed:
    top = "\N{BLACK LARGE SQUARE}" * 4
    embed = nextcord.Embed(title="2048", timestamp=date)
    embed.description = ('\n'.join([top] * 4))
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.add_field(name="points:", value=two048Points)
    embed.set_footer(text=f"coming soon")
    return embed

@bot.slash_command(name="2048", description="play a game a 2048(coming soon)", guild_ids=GUILD_IDS)
async def two_thousand_fourty_eight(interaction: nextcord.Interaction):
    embed = fourEmbed(interaction.user)

    three = Button(label="3x3", style=ButtonStyle.danger)
    four = Button(label="4x4", style=ButtonStyle.gray)
    five = Button(label="5x5", style=ButtonStyle.blurple)
    six = Button(label="6x6", style=ButtonStyle.green)
    seven = Button(label="7x7", style=ButtonStyle.primary)
    eight = Button(label="8x8", style=ButtonStyle.red)
    nine = Button(label="9x9", style=ButtonStyle.secondary)
    ten = Button(label="10x10", style=ButtonStyle.success)

    buttonViews = View(timeout=None)
    buttonViews.add_item(three)
    buttonViews.add_item(four)
    buttonViews.add_item(five)
    buttonViews.add_item(six)
    buttonViews.add_item(seven)
    buttonViews.add_item(eight)
    buttonViews.add_item(nine)
    buttonViews.add_item(ten)

    await interaction.send(view=buttonViews)
    await interaction.send(embed=embed)
#chess command

class ChessCheckersTic_Tac_ToeButtons(menus.ButtonMenu):
    def __init__(self):
        super().__init__(timeout=None)
    @nextcord.ui.button(label="Invite", style=nextcord.ButtonStyle.blurple, custom_id="ChessCheckersTic_Tac_Toe:Invite")
    async def Invite(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    @nextcord.ui.button(label="Play by Yourself", style=nextcord.ButtonStyle.secondary, custom_id="ChessCheckersTic_Tic_Toe:Yourself")
    async def Yourself(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass


def generateBoard():
    line1 = EMOJI_CODES["board_colors"]["white"] + EMOJI_CODES["board_colors"]["black"] * 4 
    line2 = EMOJI_CODES["board_colors"]["black"] + EMOJI_CODES["board_colors"]["white"] * 4
    return line1 + line2

def generateChessBoard(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Chess", timestamp=date)
    embed.description = ('\n'.join([generateBoard()] * 4))
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.add_field(name="pieces you took", value="")
    embed.add_field(name=f"pieces that {user.name} took", value="")
    embed.set_footer(text="coming soon")
    return embed

@bot.slash_command(name="chess", description="play a game of chess with a friend or a bot(coming soon)", guild_ids=GUILD_IDS)
async def chess(interaction: nextcord.Interaction):
    embed = generateChessBoard(interaction.user)
    await interaction.send(embed=embed, view=ChessCheckersTic_Tac_ToeButtons())


#checkers command

numOfCheckersPiecesPlayeOneTook = 0
numOfCheckersPiecesPlayeTwoTook = 0

def generateCheckersBoard(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Checkers", timestamp=date)
    embed.description = ('\n'.join([generateBoard()] * 4))
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.add_field(name="# of pieces you took", value=numOfCheckersPiecesPlayeOneTook)
    embed.add_field(name=f"# of pieces {user.name} took", value=numOfCheckersPiecesPlayeTwoTook)
    embed.set_footer(text="coming soon")
    return embed

@bot.slash_command(name="checkers", description="play a game of checkers with a friend or a bot(coming soon)", guild_ids=GUILD_IDS)
async def checkers(interaction: nextcord.Interaction):
    embed = generateCheckersBoard(interaction.user)
    await interaction.send(embed=embed, view=ChessCheckersTic_Tac_ToeButtons)


#snake command

SnakePoints = 0
UserSnakeHighscore = None

def generateSnakeBoard():
    return EMOJI_CODES["board_colors"]["black"] * 30

def SnakeBoard(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Snake", timestamp=date)
    embed.description = ('\n'.join([generateSnakeBoard()] * 30))
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.add_field(name="# of points", value=SnakePoints)
    embed.set_footer(text="coming soon")
    return embed

@bot.slash_command(name="snake", description="play a game of snake(coming soon)", guild_ids=GUILD_IDS)
async def snake(interaction: nextcord.Interaction):
    embed = generateSnakeBoard(interaction.user)
    await interaction.send(embed=embed)


#Tic-Tac-Toe command

def generateTTTBoard():
    return EMOJI_CODES["board_colors"]["white"] * 3

def TTTBoard(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Tic-Tac-Toe", timestamp=date)
    embed.description = ('\n'.join([generateTTTBoard()] * 3))
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(text="coming soon")
    return embed

@bot.slash_command(name="gtjnht", description="play Tic-Tac-Toe with a friend or a bot(coming soon)", guild_ids=GUILD_IDS)
async def Tic_Tac_Toe(interaction: nextcord.Interaction):
    embed = generateTTTBoard(interaction.user)
    await interaction.send(embed=embed, view=ChessCheckersTic_Tac_ToeButtons)

#random games command
#gives the user a random game when they don't know what to play

@bot.slash_command(name="Random", description="Don't know what to play?\n Why not use this", guild_ids=GUILD_IDS)
async def RandomGame(interaction: nextcord.Interaction):
    interaction.response.send_message("sorry, this command is coming soon")

def setup(bot):
    bot.add_cog(db(bot))
bot.run(os.getenv("TOKEN"))