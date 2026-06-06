from telegram import Update
from telegram.ext import CallbackContext

from commands.decorators import command
from commands.base import Command
from config.logger import log_command
from utils import try_msg


@command(member_exclusive=True)
async def slashear(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Converts a phrase into a slash-ized version
    """
    log_command(update)
    arg = cmd.get_arg_or_reply()

    words = arg.split()
    response = "/" + words[0].lower()
    for word in words[1:]:
        response += word.capitalize()
    await try_msg(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        text=response,
    )


@command(member_exclusive=True)
async def uwuspeech(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Converts a phrase into an uwu-ized version
    """
    log_command(update)
    arg = cmd.get_arg_or_reply()

    message = (
        arg.replace("r", "w")
        .replace("l", "w")
        .replace("k", "c")
        .replace("p", "pw")
        .replace("R", "W")
        .replace("L", "W")
        .replace("K", "C")
        .replace("P", "PW")
    )

    await try_msg(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        text=message,
    )


@command(member_exclusive=True)
async def repetir(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Repeats the text of a given message
    """
    log_command(update)
    arg = cmd.get_arg_or_reply()

    await try_msg(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        text=arg,
    )


@command(member_exclusive=True)
async def distancia(update: Update, context: CallbackContext) -> None:
    """
    Counts the distance between the current message and the message being replied to
    """
    log_command(update)

    message_id = update.message.message_id

    if not update.message.reply_to_message:
        return

    reply_id = update.message.reply_to_message.message_id

    answer = str(message_id - reply_id)
    mensaje_s = "mensajes" if answer != "1" else "mensaje"

    await try_msg(
        context.bot,
        chat_id=update.message.chat_id,
        parse_mode="HTML",
        text=f"{answer} {mensaje_s}",
        reply_to_message_id=message_id,
    )
