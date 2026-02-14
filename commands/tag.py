from telegram import Update
from telegram.ext import CallbackContext

import pickle
from re import match

import data
from data import persistence
from commands.decorators import command
from commands.base import Command
from config.logger import log_command
from utils import try_msg, guard_editable_bot_message, try_edit
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

tag_title = "\U0001F4A1 ATENCIÓN "


@command(member_exclusive=True)
def new_group(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Creates tag list
    """
    log_command(update)
    arg = cmd.get_arg_or_reply()
    if "%" in arg or ":" in arg:
        message = "Un grupo no puede llevar el caracter '%' o ':' en el nombre"
    elif arg:
        if "tag_groups" not in context.chat_data:
            context.chat_data["tag_groups"] = {}
        tag_groups = context.chat_data.get("tag_groups", {})
        if arg not in tag_groups:
            tag_groups[arg] = set()
            data.persistence.flush()
            message = f"Grupo {arg} creado"
        else:
            message = f"Grupo {arg} ya existe"
    else:
        message = "No me mandaste un nombre de grupo..."

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


@command(member_exclusive=True)
def group_add(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Adds a tag to a group
    """
    arg = cmd.get_arg_or_reply()
    arg = arg.split(" ")
    tag_groups = context.chat_data.get("tag_groups", {})
    if len(tag_groups) == 0:
        message = "Primero debes crear un grupo para poder agregar"
        try_msg(context.bot,
                chat_id=update.message.chat_id,
                parse_mode="HTML",
                text=message)
    else:
        keyboard = []
        tags = "%".join(arg)
        tg = list(tag_groups.keys())
        for i in range(0, len(tg)-1, 2):
            keyboard.append(
                [
                    InlineKeyboardButton(
                        tg[i], callback_data="gadd:"+tg[i]+"%"+tags),
                    InlineKeyboardButton(
                        tg[i+1], callback_data="gadd:"+tg[i+1]+"%"+tags),
                ]
            )
        if len(tg) % 2:
            keyboard.append([InlineKeyboardButton(
                tg[-1], callback_data="gadd:"+tg[-1]+"%"+tags)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Seleccione el grupo al cual agregar a \n"+"\n".join(arg), reply_markup=reply_markup)


def gadd(update, context):
    tag_groups = context.chat_data.get("tag_groups", dict())

    query = update.callback_query
    query.answer()
    answer = query.data.split(":")[1]
    answer = answer.split("%")
    group = answer[0]
    nametags = answer[1:]
    added = []
    ignored = []
    for nametag in nametags:
        if nametag not in tag_groups[group]:
            tag_groups[group].add(nametag)
            data.persistence.flush()
            added.append(nametag)
        else:
            ignored.append(nametag)
    response = "En el grupo " + group + "...\n"
    if added:
        response += "\n\U0001F4A1 Taggeare a \n- "+"\n- ".join(added)
    if ignored:
        response += "\n\U0001F44D Ya se encontraban en el grupo: \n- " + \
            "\n- ".join(ignored)
    query.edit_message_text(text=response, parse_mode="HTML")


def stag(update: Update, context: CallbackContext) -> None:
    tag_groups = context.chat_data.get("tag_groups", dict())

    query = update.callback_query
    query.answer()
    arg = query.data.split(":")[1]

    response = tag_title + arg + "!!!\n" + "\n".join(list(tag_groups[arg]))
    query.edit_message_text(text=response, parse_mode="HTML")
    return


@command(member_exclusive=True)
def rename_group(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Renames a group
    """
    log_command(update)
    arg = cmd.get_arg_or_reply()
    tag_groups = context.chat_data.get("tag_groups", dict())

    if arg == None:
        keyboard = []
        tg = list(tag_groups.keys())
        if not tg:
            update.message.reply_text("No hay grupos creados")
            return
        for i in range(0, len(tg)-1, 2):
            keyboard.append(
                [
                    InlineKeyboardButton(tg[i], callback_data="rg:"+tg[i]),
                    InlineKeyboardButton(tg[i+1], callback_data="rg:"+tg[i+1]),
                ]
            )
        if len(tg) % 2:
            keyboard.append([InlineKeyboardButton(
                tg[-1], callback_data="rg:"+tg[-1])])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Seleccione el grupo al cual renombrar:", reply_markup=reply_markup)
        return

    arg = arg.split(" ")
    if arg[0] not in tag_groups:
        response = "\U0001F44D No existe el grupo" + arg[0] + "!!1!"
    elif len(arg) != 2:
        response = "\U0001F44D Debes poner el nombre del grupo y su nuevo nombre!!1!"
    else:
        tag_groups[arg[1]] = tag_groups[arg[0]]
        tag_groups.pop(arg[0])
        data.persistence.flush()

        response = "Grupo " + arg[0] + " renombrado a " + arg[1]
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=response)


@command(member_exclusive=True)
def tag(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Tags a group
    """
    log_command(update)
    arg = cmd.get_arg_or_reply()
    tag_groups = context.chat_data.get("tag_groups", dict())

    if not arg:
        keyboard = []
        tg = list(tag_groups.keys())
        if not tg:
            update.message.reply_text("No hay grupos creados")
            return
        for i in range(0, len(tg)-1, 2):
            keyboard.append(
                [
                    InlineKeyboardButton(tg[i], callback_data="stag:"+tg[i]),
                    InlineKeyboardButton(
                        tg[i+1], callback_data="stag:"+tg[i+1]),
                ]
            )
        if len(tg) % 2:
            keyboard.append([InlineKeyboardButton(
                tg[-1], callback_data="stag:"+tg[-1])])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Seleccione el grupo al cual taggear:", reply_markup=reply_markup)
        return

    if arg not in tag_groups:
        response = "\U0001F44D No existe el grupo" + arg + "!!1!"
    else:
        response = tag_title + arg + "!!!\n" + "\n".join(list(tag_groups[arg]))
    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=response)


@command(member_exclusive=True)
def list_groups(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Lists tag groups
    """
    log_command(update)
    if "tag_groups" not in context.chat_data:
        context.chat_data["tag_groups"] = {}
    tag_groups = context.chat_data.get("tag_groups", {})
    data.persistence.flush()
    if len(tag_groups) == 0:
        message = "No hay grupos creados"
    else:
        message = "Grupos creados:"
        for g in tag_groups:
            message += "\n"+str(g)

    try_msg(context.bot,
            chat_id=update.message.chat_id,
            parse_mode="HTML",
            text=message)


@command(member_exclusive=True)
def untag(update: Update, context: CallbackContext) -> None:
    """
    Deletes the message being replied to if it was a bot tag
    """
    log_command(update)

    if guard_reply_to_message(update):
        return

    if guard_reply_to_bot_message(update, context):
        return

    if tag_title not in update.message.text:
        return

    try_delete(context.bot, chat_id=update.message.chat_id,
               message_id=update.message.reply_to_message.message_id)
