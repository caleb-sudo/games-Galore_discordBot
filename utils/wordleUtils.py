import datetime
import random
import re
from typing import List, Optional
import aiosqlite
import nextcord

from userlevel import userLevel, totalxp
from EmojiCodes import EMOJI_CODES

popular_words = open("txts/main_words.txt").read().splitlines()
all_words = set(word.strip() for word in open("txts/words.txt"))

date = datetime.datetime.now()
date.strftime("%x")

def generate_colored_word(guess: str, answer: str) -> str:
    colored_word = [EMOJI_CODES["wordle"]["gray"][letter] for letter in guess]
    guess_letters: List[Optional[str]] = list(guess)
    answer_letters: List[Optional[str]] = list(answer)
    for i in range(len(guess_letters)):
        if guess_letters[i] == answer_letters[i]:
            colored_word[i] = EMOJI_CODES["wordle"]["green"][guess_letters[i]]
            answer_letters[i] = None
            guess_letters[i] = None
    for i in range(len(guess_letters)):
        if guess_letters[i] is not None and guess_letters[i] in answer_letters:
            colored_word[i] = EMOJI_CODES["wordle"]["yellow"][guess_letters[i]]
            answer_letters[answer_letters.index(guess_letters[i])] = None
    return "".join(colored_word)


def generate_blanks() -> str:
    return "\N{WHITE MEDIUM SQUARE}" * 5


def generate_puzzle_embed(user: nextcord.User, puzzle_id: int) -> nextcord.Embed:
    embed = nextcord.Embed(title="Wordle", timestamp=date, color=0x0000FF)
    embed.description = "\n".join([generate_blanks()] * 6)
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.set_footer(
        text=f"ID: {puzzle_id} ︱ To play, use the command /games wordle!\n"
        "To guess, reply to this message with a word."
    )
    return embed


def update_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
    puzzle_id = int(embed.footer.text.split()[1])
    answer = popular_words[puzzle_id]
    colored_word = generate_colored_word(guess, answer)
    empty_slot = generate_blanks()
    embed.description = embed.description.replace(empty_slot, colored_word, 1)
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
    return word in all_words


def random_puzzle_id() -> int:
    return random.randint(0, len(popular_words) - 1)


def is_game_over(embed: nextcord.Embed) -> bool:
    return "\n\n" in embed.description


async def process_message_as_guess(bot: nextcord.Client, message: nextcord.Message) -> bool:
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
        reply = "Start a new game with /games wordle"
        if embed.author:
            reply = f"This game was started by {embed.author.name}. " + reply
        await message.reply(reply, delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    if is_game_over(embed):
        await message.reply("The game is already over. Start a new game with /games wordle", delete_after=5)
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
            f"To bypass this restriction, you can start a game with `@\u200b{bot_name} play` instead of `/games wordle`",
            delete_after=14,
        )
        try:
            await message.delete(delay=14)
        except Exception:
            pass
        return True

    if len(guess.split()) > 1:
        await message.reply("Please respond with a single 5-letter word.", delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    if not is_valid_word(guess):
        await message.reply("That is not a valid word", delete_after=5)
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