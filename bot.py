import logging
import os
import random
import re
import datetime
import aiosqlite.cursor
import nextcord
import aiosqlite

from dislevel import init_dislevel
from dislevel.utils import update_xp
from EmojiCodes import EMOJI_CODES
from dotenv import load_dotenv
from typing import List, Optional, Union, Mapping, Tuple
from nextcord.ui import Button, View, Select
from nextcord.ext import menus, commands, tasks
from userlevel import userLevel, totalxp

from utils.wordleUtils import (
    generate_puzzle_embed,
    process_message_as_guess,
    random_puzzle_id,
)
from utils.pacUtils import (
    pacLives,
    pacPoints,
    pacEmbed,
    controls,
)

from utils.nerdleUtils import (
    NerdleEmbed,
    randomNerdleEquat,
    NerdleProcessMessageAsGuess,
)

from utils.binaryNerdle import (
    binaryNerdleEmbed,
    randomBinaryNerdleEquat,
    binaryNerdleProcessMessageAsGuess
)

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def on_ready(self):
        print(f"-----\nLogged in as: {self.user.name} : {self.user.id}\n-----")



load_dotenv()
activity = nextcord.Activity(name='', type=nextcord.ActivityType.listening)
bot = Bot(command_prefix=commands.when_mentioned_or("w?"), activity=activity, intents=nextcord.Intents.all())

date = datetime.datetime.now()
date.strftime("%x")

GUILD_IDS = (
    [int(guild_id) for guild_id in os.getenv("GUILD_IDS", "").split(",")]
    if os.getenv("GUILD_IDS", None)
    else nextcord.utils.MISSING
)

class mainButtons(nextcord.ui.Button):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y
    async def callback(self, interaction: nextcord.Interaction):
        assert self.view is not None
        view: tetrisGame = self.view
        state = view.board[self.y][self.x]
        if state in (view.up, view.left, view.right, view.down):
            return
        
        if view.up:
            self.emoji = '⬆️'
            self.style = nextcord.ButtonStyle.blurple
            view.board[self.y][self.x] = view.up
        if view.down:
            self.emoji = '⬇️'
            self.style = nextcord.ButtonStyle.blurple
            view.board[self.y][self.x] = view.down
        if view.left:
            self.emoji = '⬅️'
            self.style = nextcord.ButtonStyle.blurple
            view.board[self.y][self.x] = view.left
        if view.right:
            self.emoji = '➡️'
            self.style = nextcord.ButtonStyle.blurple
            view.board[self.y][self.x] = view.right

Wordle = 'Wordle'
@bot.slash_command(guild_ids=GUILD_IDS)
async def games(interaction: nextcord.Interaction):
    pass


#wordle command
gamesplayed = 1
@games.subcommand(name="wordle", description="Play a game of Wordle")
async def wordle(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    embed = generate_puzzle_embed(interaction.user, random_puzzle_id())
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(Wordle), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user), int(interaction.user.id), int(gamesplayed))
            await cursor.execute(insert, vals)
        await db.commit()
    await interaction.send(embed=embed)

@bot.event
async def on_message(message: nextcord.Message):
    processed_as_guess = await process_message_as_guess(bot, message)
    if not processed_as_guess:
        await bot.process_commands(message)

binWordle = "binary_wordle"
@games.subcommand(name="binary_wordle", description="Play a game of wordle, but the letters are in binary")
async def binaryWordle(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(binWordle), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user), int(interaction.user.id), int(gamesplayed))
            await cursor.execute()
        await db.commit()

@bot.event
async def on_message(message: nextcord.Message):
    pass

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

class tetrisGame(nextcord.ui.View):
    children: List[mainButtons]
    
    up = 1
    left = 2
    right = 3
    down = 4
    
    def __init__(self):
        super().__init__()
        self.board = [
            [0, 1, 0],
            [2, 0, 3],
            [0, 4, 0],
        ]
        for x in range(3):
            for y in range(3):
                self.add_item(mainButtons(x, y))

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
    blocks.S_block(),
]

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
    embed = nextcord.Embed(title="Tetris", timestamp=date, color=0x0000FF)
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
            
Tetris = "Tetris"
@games.subcommand(name="tetris", description="play a game of tetris(coming soon)")
async def tetris(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    embed = generate_map_tetris(interaction.user.id)
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(Tetris), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user), int(interaction.user.id), int(gamesplayed))
            await cursor.execute(insert, vals)
        await db.commit()
    await interaction.send(embed=embed)


#nerdle command
Nerdle = "Nerdle"
@games.subcommand(name="nerdle", description="play a game of nerdle, which it just like wordle\n but with maths")
async def nerdle(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(Nerdle), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user), int(interaction.user.id), int(gamesplayed))
            await cursor.execute(insert, vals)
        await db.commit()
    
    async def dropdownCallback(interaction: nextcord.Interaction):
        for value in dropdown.values:
            pass
        
    embed = NerdleEmbed(interaction.user, randomNerdleEquat())
    normal = nextcord.SelectOption(label="normal", description="play the normal version of nerdle", value="normal")
    binary = nextcord.SelectOption(label="binary", description="play nerdle but all the numbers are in binary", value="binary")
    dropdown = Select(placeholder="Version", max_values=1, options=[normal, binary])
    dropdown.callback = dropdownCallback
    menu = View(timeout=None)
    menu.add_item(dropdown)
    await interaction.send(embed=embed)

@bot.event
async def on_message(message: nextcord.Message):
    processedAsGuess = await NerdleProcessMessageAsGuess(bot, message)
    if not processedAsGuess:
        await bot.process_commands(message)


binNerdle = "Binary Nerdle"
#binary nerdle
@games.subcommand(name="nerdlebinary", description="nerdle but in Binary")
async def binaryNerdle(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(binNerdle), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user), int(interaction.user.id), int(gamesplayed))
            await cursor.execute(insert, vals)
        await db.commit()
    embed = binaryNerdleEmbed(interaction.user, randomBinaryNerdleEquat())
    await interaction.send(embed=embed)

@bot.event 
async def on_message(message: nextcord.Message):
    processAsGuess = await binaryNerdleProcessMessageAsGuess(bot, message)
    if not processAsGuess:
        await bot.process_commands(message)

#2048 command

two048Points = 0
User2048Highscore = None

#2048 grid sizes selection menu
possible2048startingBlocks = [
    EMOJI_CODES['2048']['2'],
    EMOJI_CODES['2048']['4'],
]  
def random2048startingBlocks():
    return random.choices(possible2048startingBlocks)

async def fourEmbed(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="2048", timestamp=date, color=0x0000FF)
    embed.description = ('\n'.join([random2048startingBlocks()] * 4))
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.add_field(name="points:", value=two048Points)
    embed.set_footer(text=f"coming soon")
    return embed

@games.subcommand(name="2048", description="play a game a 2048(coming soon)")
async def two_thousand_fourty_eight(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    embed = fourEmbed(interaction.user)
    
    three = Button(label="3x3", style=nextcord.ButtonStyle.danger)
    four = Button(label="4x4", style=nextcord.ButtonStyle.gray)
    five = Button(label="5x5", style=nextcord.ButtonStyle.blurple)
    six = Button(label="6x6", style=nextcord.ButtonStyle.green)
    seven = Button(label="7x7", style=nextcord.ButtonStyle.primary)
    eight = Button(label="8x8", style=nextcord.ButtonStyle.red)
    nine = Button(label="9x9", style=nextcord.ButtonStyle.secondary)
    ten = Button(label="10x10", style=nextcord.ButtonStyle.success)

    buttonViews = View(timeout=None)
    buttonViews.add_item(three)
    buttonViews.add_item(four)
    buttonViews.add_item(five)
    buttonViews.add_item(six)
    buttonViews.add_item(seven)
    buttonViews.add_item(eight)
    buttonViews.add_item(nine)
    buttonViews.add_item(ten)
    
    await interaction.send(embed=embed, view=buttonViews)
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
    return EMOJI_CODES["board_colors"]["white"] + EMOJI_CODES["board_colors"]["black"] + EMOJI_CODES["board_colors"]["white"] + EMOJI_CODES["board_colors"]["black"] + EMOJI_CODES["board_colors"]["white"] + EMOJI_CODES["board_colors"]["black"] + EMOJI_CODES["board_colors"]["white"] + EMOJI_CODES["board_colors"]["black"] + "\n" + EMOJI_CODES["board_colors"]["black"] + EMOJI_CODES["board_colors"]["white"] + EMOJI_CODES["board_colors"]["black"] + EMOJI_CODES["board_colors"]["white"] + EMOJI_CODES["board_colors"]["black"] + EMOJI_CODES["board_colors"]["white"] + EMOJI_CODES["board_colors"]["black"] + EMOJI_CODES["board_colors"]["white"]

def generateChessBoard(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Chess", timestamp=date)
    embed.description = ('\n'.join([generateBoard()] * 4))
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.add_field(name="pieces you took", value="")
    embed.add_field(name=f"pieces that {user.name} took", value="")
    embed.set_footer(text="coming soon")
    return embed

Chess = "Chess"
@games.subcommand(name="chess", description="play a game of chess with a friend or a bot(coming soon)")
async def chess(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(Chess), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user.name), int(interaction.user.id), int(gamesplayed))
            #await cursor.execute(insert, vals)
        await db.commit()
    embed = generateChessBoard(interaction.user)
    await interaction.send(embed=embed, view=ChessCheckersTic_Tac_ToeButtons())


#checkers command

numOfCheckersPiecesPlayeOneTook = 0 
numOfCheckersPiecesPlayeTwoTook = 0

def generateCheckersBoard(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Checkers", timestamp=date)
    embed.description = ('\n'.join([generateBoard()] * 4))
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.add_field(name="# of pieces you took", value=numOfCheckersPiecesPlayeOneTook)
    embed.add_field(name=f"# of pieces {user.name} took", value=numOfCheckersPiecesPlayeTwoTook)
    embed.set_footer(text="coming soon")
    return embed

check = "Checkers"
@games.subcommand(name="checkers", description="play a game of checkers with a friend or a bot(coming soon)")
async def checkers(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(check), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user.name), int(interaction.user.id), int(gamesplayed))
            #await cursor.execute(insert, vals)
        await db.commit()
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
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.add_field(name="# of points", value=SnakePoints)
    embed.set_footer(text="coming soon")
    return embed

snake = "Snake"
@games.subcommand(name="snake", description="play a game of snake(coming soon)")
async def snake(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(snake), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user.name), int(interaction.user.id), int(gamesplayed))
            #await cursor.execute(insert, vals)
        await db.commit()
    embed = generateSnakeBoard(interaction.user)
    await interaction.send(embed=embed)


#pacman command

optOneEmote = EMOJI_CODES["pacman"]["pacman_skins"]["pacman_normal"]["up"]
optTwoEmote = EMOJI_CODES["pacman"]["pacman_skins"]["pacman_8bit"]["up"]
optThreeEmote = EMOJI_CODES["pacman"]["pacman_skins"]["pacman_teeth"]["up"]
optFourEmote = EMOJI_CODES["pacman"]["pacman_skins"]["ms_pacman"]["up"]
Pacman = "Pacman"
@games.subcommand(name="pacman", description="play a game of pacman")
async def pacman(interaction: nextcord.Interaction):
    PacmanEmbed = pacEmbed(interaction.user)
    async def dropdownCallback(interaction: nextcord.Interaction):
        for value in dropdown.values:
            pass
    
    async def startCallback(interaction: nextcord.Interaction):
        await interaction.response.send_message(embed=PacmanEmbed, view=controls())
        
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
        
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(Pacman), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user), int(interaction.user.id), int(gamesplayed))
            await cursor.execute(insert, vals)
        await db.commit()
    
    optOne = nextcord.SelectOption(label="normal pacman", value="normal")
    optTwo = nextcord.SelectOption(label="8bit pacman", value="bit")
    optThree = nextcord.SelectOption(label="pacman with sharp teeth", value="teeth")
    optFour = nextcord.SelectOption(label="Ms. Pacman", value="ms")
    randomPacman = nextcord.SelectOption(label="random", value="randomPacman")
    
    dropdown = Select(placeholder="choose your pacman skin", max_values=1, options=[optOne, optTwo, optThree, optFour, randomPacman])
    
    start = Button(label="ready?", style=nextcord.ButtonStyle.blurple,)
    
    dropdown.callback = dropdownCallback
    start.callback = startCallback
    select = View(timeout=30)
    select.add_item(dropdown)
    select.add_item(start)
    await interaction.send(view=select)


#sudoku command

def sudokuBoard():
    return "\N{WHITE LARGE SQUARE}" * 9 

def sudokuEmbed(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="Sudoku", timestamp=date)
    embed.description = ('\n'.join([sudokuBoard()] * 9))
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.set_footer(text="coming soon")
    return embed

sudok = "Sudoku"

@games.subcommand(name="sudoku", description="play a game of sudoku")
async def sudoku(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(sudok), int(interaction.guild_id), str(interaction.guild.name), str(interaction.user.name), str(interaction.user.id), int(gamesplayed))
            #await cursor.execute(insert, vals)
        await db.commit()
    embed = sudokuEmbed(interaction.user)
    await interaction.send(embed=embed)


#minesweeper command

class minesweeperButtons(nextcord.ui.Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=nextcord.ButtonStyle.gray, label='\u200b', row=y)
        self.x = x
        self.y = y
    async def callback(self, interaction: nextcord.Interaction):
        assert self.view is not None
        view: minesweeperGame = self.view
        state = view.board[self.y][self.x]
        randomTile = [
            view.flag,
            view.bomb,
            view.one,
            view.two,
            view.three,
            view.four,
            view.five,
            view.six,
            view.seven,
            view.eight,
        ]
        if state in (view.flag, view.bomb, view.one, view.two, view.three, view.four, view.five, view.six, view.seven, view.eight):
            return
        if view.current_player == view.flag:
            self.content = 'you Win!'
            self.disabled = True
            self.emoji = EMOJI_CODES["minesweeper"]["flag"]
            view.board[self.y][self.x] = view.flag
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.bomb:
            self.content = 'you lose\nGood luck next time!'
            self.disabled = True
            self.emoji = EMOJI_CODES["minesweeper"]
            view.board[self.y][self.x] = view.bomb
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.one:
            self.disabled = True
            self.style = nextcord.ButtonStyle.danger
            self.label = "1"
            self.content = "closest bomb(s) 1 tile away"
            view.board[self.y][self.x] = view.one
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.two:
            self.disabled = True
            self.style = nextcord.ButtonStyle.red
            self.label = "2"
            self.content = "closest bomb(s) 2 tiles away"
            view.board[self.y][self.x] = view.two
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.three:
            self.disabled = True
            self.style = nextcord.ButtonStyle.green
            self.label = "3"
            self.content = "closest bomb(s) 3 tiles away"
            view.board[self.y][self.x] = view.three
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.four:
            self.disabled = True
            self.style = nextcord.ButtonStyle.success
            self.label = "4"
            self.content = "closest bomb(s) 4 tiles away"
            view.board[self.y][self.x] = view.four
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.five:
            self.disabled = True
            self.style = nextcord.ButtonStyle.gray
            self.label = "5"
            self.content = "closest bomb(s) 5 tiles away"
            view.board[self.y][self.x] = view.five
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.six:
            self.disabled = True
            self.style = nextcord.ButtonStyle.blurple
            self.label = "6"
            self.content = "closest bomb(s) 6 tiles away"
            view.board[self.y][self.x] = view.six
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.seven:
            self.disabled = True
            self.style = nextcord.ButtonStyle.primary
            self.label = "7"
            self.content = "closest bomb(s) 7 tiles away"
            view.board[self.y][self.x] = view.seven
            view.current_player = random.choice(randomTile)
        elif view.current_player == view.eight:
            self.disabled = True
            self.style = nextcord.ButtonStyle.secondary
            self.label = "8"
            self.content = "closest bomb(s) 8 tiles away"
            view.board[self.y][self.x] = view.eight
            view.current_player = random.choice(randomTile)
        
        await interaction.response.edit_message(view=view)   
class minesweeperGame(nextcord.ui.View):
    children: List[minesweeperButtons]
    flag = -1
    bomb = 1
    one = 2
    two = 3
    three = 4
    four = 5
    five = 6
    six = 7
    seven = 8
    eight = 9
    
    def __init__(self):
        super().__init__()
        self.current_player = self.one
        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        for x in range(5):
            for y in range(5):
                self.add_item(minesweeperButtons(x, y))
    
    #def checkWinner(self):
        

mine = "Minesweeper"
@games.subcommand(name="minesweeper", description="play a game of minesweeper")
async def minesweeper(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO user{interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(mine), int(interaction.user.id), str(interaction.user.name), str(interaction.user.name), int(interaction.user.id), int(gamesplayed))
            #await cursor.execute(insert, vals)
        await db.commit() 
    await interaction.send(view=minesweeperGame())

#Tic-Tac-Toe command

class TicTacToe_Buttons(nextcord.ui.Button["TicTacToeGame"]):
    def __init__(self, x: int, y: int):
        super().__init__(style=nextcord.ButtonStyle.blurple, label='\u200b', row=y)
        self.x = x
        self.y = y
    
    async def callback(self, interaction: nextcord.Interaction):
        assert self.view is not None
        view: TicTacToeGame = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return
        if view.current_player == view.X:
            self.style = nextcord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = nextcord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"
            
        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)   
        
class TicTacToeGame(nextcord.ui.View):
    children: List[TicTacToe_Buttons]
    X = -1
    O = 1
    Tie = 2
    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToe_Buttons(x, y))
                
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

tic = "Tic-Tac-Toe"
@games.subcommand(name="tic_tac_toe", description="Play a game of Tic-Tac-Toe")
async def TicTacToe(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"CREATE TABLE IF NOT EXISTS {interaction.user} (game VARCHAR(255), guild_id INT, guild_name VARCHAR(255), user VARCHAR(255), user_id INT, games_played VARCHAR(255))")
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            insert = f"INSERT INTO {interaction.user} (game, guild_id, guild_name, user, user_id, games_played) VALUES (?, ?, ?, ?, ?, ?)"
            vals = (str(tic), int(interaction.user.id), str(interaction.user.name), str(interaction.user.name), int(interaction.user.id), int(gamesplayed))
            await cursor.execute(insert, vals)
        await db.commit()
    await interaction.send('Tic-Tac-Toe: X goes first', view=TicTacToeGame())

#info commands

def infoEmbed(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(title="info", timestamp=date)
    embed.add_field(name="games\n", value="\n\n/games wordle\n/games tetris\n/games nerdle\n/games nerdlebinary\n/games 2048\n/games chess\n/games checkers\n/games snake\ngames pacman\ngames sudoku\ngames minesweeper\n/tic_tac_toe")
    embed.add_field(name="others\n", value="\n\n/played\n/user_played\n/stats\n/chaos\n/reportbugs_or_feedback")
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    return embed

@bot.slash_command(name="commands_info", description="commands list", guild_ids=GUILD_IDS)
async def commandInfo(interaction: nextcord.Interaction):
    embed = infoEmbed(interaction.user)
    await interaction.send(embed=embed)

@bot.slash_command(name="played", description="displays your highscores or highest win streak, in games you've played", guild_ids=GUILD_IDS)
async def highscores(interaction: nextcord.Interaction):
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM 'main'.sqlite_master;")
            fetchTablesCount = await cursor.fetchall()
        await db.commit()
        
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Wordle' AND guild_id = '{interaction.guild_id}'")
            WordleFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Tetris' AND guild_id = '{interaction.guild_id}'")
            TetrisFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Nerdle' AND guild_id = '{interaction.guild_id}'")
            NerdleFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = '2048' AND  guild_id = '{interaction.guild_id}'")
            TwozeroFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Chess' AND guild_id = '{interaction.guild_id}'")
            ChessFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Checkers' AND guild_id = '{interaction.guild_id}'")
            CheckersFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Snake' AND guild_id = '{interaction.guild_id}'")
            SnakeFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Pacman' AND guild_id = '{interaction.guild_id}'")
            PacmanFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Sudoku' AND guild_id = '{interaction.guild_id}'")
            sudokuFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Minesweeper' AND guild_id = '{interaction.guild_id}'")
            MinesweeperFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'binary_nerdle' AND guild_id = '{interaction.guild_id}'")
            binaryNerdleFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'binary_wordle' AND guild_id = '{interaction.guild_id}'")
            binaryWordleFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE game = 'Tic-Tac-Toe' AND guild_id = '{interaction.guild_id}'")
            ticFetch = await cursor.fetchall()
        await db.commit()
    async with aiosqlite.connect("mainDB.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT sum(games_played) FROM {interaction.user} WHERE guild_id = '{interaction.guild_id}'")
            TotalFetch = await cursor.fetchall()
        await db.commit()

    wordleMod = str(WordleFetch).replace('[(', '').replace(',)]', '')
    tetrisMod = str(TetrisFetch).replace('[(', '').replace(',)]', '')
    nerdleMod = str(NerdleFetch).replace('[(', '').replace(',)]', '')
    twozeroMod = str(TwozeroFetch).replace('[(', '').replace(',)]', '')
    chessMod = str(ChessFetch).replace('[(', '').replace(',)]', '')
    checkersMod = str(CheckersFetch).replace('[(', '').replace(',)]', '')
    snakeMod = str(SnakeFetch).replace('[(', '').replace(',)]', '')
    pacmanMod = str(PacmanFetch).replace('[(', '').replace(',)]', '')
    sudokuMod = str(sudokuFetch).replace('[(', '').replace(',)]', '')
    minesweeperMod = str(MinesweeperFetch).replace('[(', '').replace(',)]', '')
    binaryNerdleMod = str(binaryNerdleFetch).replace('[(', '').replace(',)]', '')
    binaryWordleMod = str(binaryWordleFetch).replace('[(', '').replace(',)]', '')
    ticMod = str(ticFetch).replace('[(', '').replace(',)]', '')
    totalMod = str(TotalFetch).replace('[(', '').replace(',)]', '')
    #i = 0
    #while i <= 1:
        #opts = [
            #nextcord.SelectOption(label=f"{fetchTableName[i]}")
        #]
        #dropdown = Select(placeholder="user", max_values=1, options=[opts[i]])
        #i+=1
    
    #select = View(timeout=30)
    #select.add_item(dropdown)
    embed = nextcord.Embed(title=f"{interaction.user}'s games played", timestamp=date, color=0x0000FF)
    embed.add_field(name="Wordle", value=wordleMod, inline=False, )
    embed.add_field(name="binary wordle", value=binaryWordleMod, inline=False)
    embed.add_field(name="Tetris", value=tetrisMod, inline=False)
    embed.add_field(name="Nerdle", value=nerdleMod, inline=False)
    embed.add_field(name="binary Nerdle", value=binaryNerdleMod, inline=False)
    embed.add_field(name="2048", value=twozeroMod, inline=False)
    embed.add_field(name="Chess", value=chessMod, inline=False)
    embed.add_field(name="Checkers", value=checkersMod, inline=False)
    embed.add_field(name="Snake", value=snakeMod, inline=False)
    embed.add_field(name="Sudoku", value=pacmanMod, inline=False)
    embed.add_field(name="Pacman", value=sudokuMod, inline=False)
    embed.add_field(name="minesweeper", value=minesweeperMod, inline=False)
    embed.add_field(name="Tic-Tac-Toe", value=ticMod, inline=False)
    embed.add_field(name="total", value=totalMod, inline=False)
    embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
    await interaction.send(embed=embed)


class selectPlayed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @bot.slash_command(name="user_played", description="like /played but you can select a different user to see", guild_ids=GUILD_IDS)
    async def userPlayed(self, interaction: nextcord.Interaction, choices: str):
        async with aiosqlite.connect("mainDB.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT tbl_name FROM 'main'.sqlite_master;")
                global fetchTableName
                fetchTableName = await cursor.fetchall()
            await db.commit()
        nextcord.SlashOption(name="select user", choices={fetchTableName})
        await interaction.response.send_message(choices)
        
def statsEmbed(interaction: nextcord.Interaction) -> nextcord.Embed:
    embed = nextcord.Embed(title="stats", timestamp=date)
    embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
    return embed

@bot.slash_command(name="stats", description="bot stats", guild_ids=GUILD_IDS)
async def stats(interaction: nextcord.Interaction):
    embed = statsEmbed(interaction.user)
    await interaction.send(embed=embed)

@bot.slash_command(name="chaos", description="chaos, do not use or else...", guild_ids=GUILD_IDS)
async def chaos(interaction: nextcord.Interaction):
    await bot.wait_until_ready()
    #test = interaction.guild_locale
    #await interaction.send(test)
    for user in bot.users:
        users = user.mention
        await interaction.send(f"{users}")

class reportModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="report any bugs or issues",
            timeout=60,
        )
        
        self.issue = nextcord.ui.TextInput(
            label="Issue",
            style=nextcord.TextInputStyle.short,
            placeholder="write what the problem, here",
            required=True,
        )
        self.add_item(self.issue)
        
        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            min_length=20,
            placeholder="describe what the issue of bug is causing, here"
        )
        self.add_item(self.description)

        self.commands = nextcord.ui.TextInput(
            label="affected commands",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            min_length=5,
            placeholder="give the names of all the commands that are affected by this issue or bug, here"
        )
        
        self.add_item(self.commands)
        
    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.send_message(f"Thank you for your time, {interaction.user.nick}")
        async with aiosqlite.connect("mainDB.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS issues (Issue VARCHAR(255), description VARCHAR(255), commands_affected VARCHAR(255), user VARCHAR(255), user_id INTEGER)")
            await db.commit()
        async with aiosqlite.connect("mainDB.db") as db:
            async with db.cursor() as cursor:
                insert = "INSERT INTO issues (Issue, description, commands_affected, user, user_id) VALUES (?, ?, ?, ?, ?)"
                vals = (str(self.issue.value), str(self.description.value), str(self.commands.value), str(interaction.user), int(interaction.user.id))
                await cursor.execute(insert, vals)
            await db.commit()
            
class feedbackModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Feedback",
            timeout=60,
        )
    
        self.feedback = nextcord.ui.TextInput(
            label="Feedback",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            min_length=30,
            max_length=250,
            placeholder="give your feedback, here"
        )
        self.add_item(self.feedback)
        
    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.send_message(f"Thank you for your time, {interaction.user.nick}")
        async with aiosqlite.connect("mainDB.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS feedback (Feedback VARCHAR(255), user VARCHAR(255), user_id INTEGER)")
            db.commit()
        async with aiosqlite.connect("mainDB.db") as db:
            async with db.cursor() as cursor:
                insert = "INSERT INTO feedback (Feedback, user, user_id) VALUES (?, ?, ?)"
                vals = (str(self.feedback.value), str(interaction.user), int(interaction.user.id))
                await cursor.execute(insert, vals)
            await db.commit()

class IdeasModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Ideas",
            timeout=60,
        )
        
        self.idea = nextcord.ui.TextInput(
            label="Idea",
            style=nextcord.TextInputStyle.short,
            required=True,
            min_length=5,
            max_length=100,
            placeholder="Write the concept of your idea, here",
        )
        self.add_item(self.idea)
        
        self.description = nextcord.ui.TextInput(
            label="Description of your idea",
            style=nextcord.TextInputStyle.paragraph,
            min_length=40,
            max_length=300,
            placeholder="Write a breif description of your idea, here",
        )
        self.add_item(self.description)
        
    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.send_message(f"thank you for your time, {interaction.user.nick}")
        async with aiosqlite.connect("mainDB.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS ideas (Idea VARCHAR(255), description VARCHAR(255), user VARCHAR(255), user_id INTEGER)")
            await db.commit()
        async with aiosqlite.connect("mainDB.db") as db:
            async with db.cursor() as cursor:
                insert = "INSERT INTO ideas (Idea, description, user, user_id) VALUES (?, ?, ?, ?)"
                vals = (str(self.idea.value), str(self.description.value), str(interaction.user), int(interaction.user.id))
                await cursor.execute(insert, vals)
            await db.commit()

class bugOrFeedback(nextcord.ui.View):
    def __init__(self):
        super().__init__()
    
    @nextcord.ui.button(label="report a bug or issue", style=nextcord.ButtonStyle.blurple)
    async def bugOrIssue(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        return await interaction.response.send_modal(reportModal())
    
    @nextcord.ui.button(label="Feedback", style=nextcord.ButtonStyle.green)
    async def feedback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        return await interaction.response.send_modal(feedbackModal())
    
    @nextcord.ui.button(label="Ideas", style=nextcord.ButtonStyle.success)
    async def ideas(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        return await interaction.response.send_modal(IdeasModal())
    
@bot.slash_command(name="reportbugs_or_feedback", description=f"report any bugs or issues you come across here, or you can give feedback, or any ideas you have that could help improve the bot", guild_ids=GUILD_IDS)
async def report(interaction: nextcord.Interaction):
    await interaction.send(view=bugOrFeedback())

class leaderboards(commands.Cog):
    def __init__(self):
        self.bot = bot
    
    class pagnate(menus.ListPageSource):
        def __init__(self, leaders):
            super().__init__(leaders, per_page=5)
        
        async def formatPage(self, menu, entries, user: nextcord.User) -> nextcord.Embed:
            async with aiosqlite.connect("mainDB.db") as db:
                async with db.cursor() as cursor:
                    pass
                await db.commit()
            embed = nextcord.Embed(title="Leaders", timestamp=date)
            embed.add_field(name="1:", value="")
            embed.add_field(name="2:", value="")
            embed.add_field(name="3:", value="")
            embed.add_field(name="4:", value="")
            embed.add_field(name="5:", value="")
            embed.set_author(name=user.name, icon_url=user.avatar.url)
            return embed
    
    @bot.slash_command(name="leaderboards", description="displays the leaderboards for all of games galore!'s games", guild_ids=GUILD_IDS)
    async def leaderboards(self, interaction: nextcord.Interaction):
        pass

bot.add_cog(leaderboards(bot))
bot.add_cog(selectPlayed(bot))    
bot.run(os.getenv("TOKEN"))