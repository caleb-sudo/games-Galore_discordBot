import datetime
import random
import re
from typing import List, Optional
import aiosqlite
import nextcord

from EmojiCodes import EMOJI_CODES

date = datetime.datetime.now()
date.strftime("%x")

equats = open("txts/equations_nerdle.txt").read().splitlines()

def generate_coloredNum(guess: str, answer: str) -> str:
    coloredNum = [EMOJI_CODES["nerdle"]["binary"]["gray"][number] for number in guess]
    guessNumbers: List[Optional[str]] = list(guess)
    answerNumbers: List[Optional[str]] = list(answer)
    for i in range(len(guessNumbers)):
        if guessNumbers[i] == answerNumbers[i]:
            coloredNum[i] = EMOJI_CODES["nerdle"]["binary"]["green"][guessNumbers[i]]
            answerNumbers[i] = None
            guessNumbers[i] = None
    for i in range(len(guessNumbers)):
        if guessNumbers[i] is not None and guessNumbers[i] in answerNumbers:
            coloredNum[i] = EMOJI_CODES["nerdle"]["binary"]["yellow"][guessNumbers[i]]
            answerNumbers[answerNumbers.index(guessNumbers[i])] = None
    return "".join(coloredNum)

def generate_blanks() -> str:
    return "\N{WHITE MEDIUM SQUARE}" * 8

def binaryNerdleEmbed(user: nextcord.User, puzzle_id: int) -> nextcord.Embed:
    embed = nextcord.Embed(title="Nerdle", timestamp=date, color=0x0000FF)
    embed.description = "\n".join([generate_blanks()] * 6)
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.set_footer(
        text=f"ID: {puzzle_id} ︱ To play, use the command /games nerdlebinary!\n"
        "To guess, reply to this message with a word."
    )
    return embed

def update_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
    puzzle_id = int(embed.footer.text.split()[1])
    answer = equats[puzzle_id]
    coloredNum = generate_coloredNum(guess, answer)
    empty_slot = generate_blanks()
    embed.description = embed.description.replace(empty_slot, coloredNum, 1)
    num_empty_slots = embed.description.count(empty_slot)
    if guess == answer:
        if num_empty_slots == 0:
            embed.description += "\n\nPhew!"
        if num_empty_slots == 1:
            embed.description += "\n\nGreat!"
        if num_empty_slots == 2:
            embed.description += "\n\nSplendid!"
        if num_empty_slots == 3:
            embed.description += "\n\nImpressive!"
        if num_empty_slots == 4:
            embed.description += "\n\nMagnificent!"
        if num_empty_slots == 5:
            embed.description += "\n\nGenius!"
    elif num_empty_slots == 0:
        embed.description += f"\n\nThe answer was {answer}!"
    return embed


def is_valid_word(word: str) -> bool:
    return word in equats

def randomBinaryNerdleEquat() -> int:
    return random.randint(0, len(equats) - 1)

def is_game_over(embed: nextcord.Embed) -> bool:
    return "\n\n" in embed.description

async def binaryNerdleProcessMessageAsGuess(bot: nextcord.Client, message: nextcord.Message) -> bool:
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
        reply = "Start a new game with /games nerdlebinary"
        if embed.author:
            reply = f"This game was started by {embed.author.name}. " + reply
        await message.reply(reply, delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    if is_game_over(embed):
        await message.reply("The game is already over. Start a new game with /games nerdlebinary", delete_after=5)
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
            "Please try mentioning me in your reply before the equation you want to guess.\n\n"
            f"**For example:**\n{bot.user.mention} 11+11=22\n\n"
            f"To bypass this restriction, you can start a game with `@\u200b{bot_name} play` instead of `/games nerdlebinary`",
            delete_after=14,
        )
        try:
            await message.delete(delay=14)
        except Exception:
            pass
        return True

    if len(guess.split()) > 1:
        await message.reply("Please respond with a single 6 character equation", delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    if not is_valid_word(guess):
        await message.reply("That is not a valid equation", delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    embed = update_embed(embed, guess)
    await parent.edit(embed=embed)

    try:
        await message.delete()
    except Exception:
        pass

    return True