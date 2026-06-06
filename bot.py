from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler

import data

from core import application
from config.auth import admin_ids, group_id, debug

from commands.admin import get_log, prohibir
from commands.counter import contador, sumar, restar
from commands.list import lista, agregar, quitar, editar, deslistar
from commands.text import slashear, uwuspeech, repetir, distancia
from commands.response import start, tup, gracias, weekly_poll, reply_hello
from commands.tag import group_add, new_group, gadd, tag, list_groups, untag, stag, rename_group


def main():
    # Admin
    application.add_handler(CommandHandler("get_log", get_log,
                             filters=filters.User(user_id=admin_ids)))
    application.add_handler(CommandHandler("prohibir", prohibir,
                             filters=filters.User(user_id=admin_ids)))

    # Counter
    application.add_handler(CommandHandler("contador", contador))
    application.add_handler(CommandHandler(["sumar", "incrementar"], sumar))
    application.add_handler(CommandHandler(["restar", "decrementar"], restar))

    # List
    application.add_handler(CommandHandler(["lista", "listar"], lista))
    application.add_handler(CommandHandler("agregar", agregar))
    application.add_handler(CommandHandler("quitar", quitar))
    application.add_handler(CommandHandler("editar", editar))
    application.add_handler(CommandHandler(["deslistar", "cerrar"], deslistar))

    # Response
    application.add_handler(CommandHandler("tup", tup))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler(["gracias", "garcias"], gracias))
    application.add_handler(CommandHandler("asistencia", weekly_poll))
    application.add_handler(CommandHandler("hello", reply_hello))

    # Tag
    application.add_handler(CallbackQueryHandler(gadd, pattern='gadd:.*'))
    application.add_handler(CommandHandler("group_add", group_add))
    application.add_handler(CommandHandler("new_group", new_group))
    application.add_handler(CommandHandler("tag", tag))
    application.add_handler(CommandHandler("list_groups", list_groups))
    application.add_handler(CommandHandler("untag", untag))
    application.add_handler(CallbackQueryHandler(stag, pattern='stag:.*'))
    application.add_handler(CommandHandler("rename_group", rename_group))

    application.run_polling()


if __name__ == "__main__":
    main()
