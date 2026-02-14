from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import data

from core import updater, dp
from config.auth import admin_ids, group_id, debug

from commands.admin import get_log, prohibir
from commands.counter import contador, sumar, restar
from commands.list import lista, agregar, quitar, editar, deslistar
from commands.text import slashear, uwuspeech, repetir, distancia
from commands.response import start, tup, gracias, weekly_poll, reply_hello
from commands.tag import group_add, new_group, gadd, tag, list_groups, untag, stag, rename_group


def main():
    # Admin
    dp.add_handler(CommandHandler("get_log", get_log,
                   filters=Filters.user(admin_ids)))
    dp.add_handler(CommandHandler("prohibir", prohibir,
                   filters=Filters.user(admin_ids)))

    # Counter
    dp.add_handler(CommandHandler("contador", contador))
    dp.add_handler(CommandHandler(["sumar", "incrementar"], sumar))
    dp.add_handler(CommandHandler(["restar", "decrementar"], restar))

    # List
    dp.add_handler(CommandHandler(["lista", "listar"], lista))
    dp.add_handler(CommandHandler("agregar", agregar))
    dp.add_handler(CommandHandler("quitar", quitar))
    dp.add_handler(CommandHandler("editar", editar))
    dp.add_handler(CommandHandler(["deslistar", "cerrar"], deslistar))

    # Response
    dp.add_handler(CommandHandler("tup", tup))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler(["gracias", "garcias"], gracias))
    dp.add_handler(CommandHandler("asistencia", weekly_poll))
    dp.add_handler(CommandHandler("hello", reply_hello))

    # Tag
    dp.add_handler(CallbackQueryHandler(gadd, pattern='gadd:.*'))
    dp.add_handler(CommandHandler("group_add", group_add))
    dp.add_handler(CommandHandler("new_group", new_group))
    dp.add_handler(CommandHandler("tag", tag))
    dp.add_handler(CommandHandler("list_groups", list_groups))
    dp.add_handler(CommandHandler("untag", untag))
    dp.add_handler(CallbackQueryHandler(stag, pattern='stag:.*'))
    dp.add_handler(CommandHandler("rename_group", rename_group))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
