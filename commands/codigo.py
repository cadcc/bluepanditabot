import html
import re
from typing import List, Optional, Tuple

import httpx
from telegram import Update
from telegram.ext import CallbackContext

from commands.base import Command
from commands.decorators import command
from config import mufasa
from config.logger import logger
from utils import try_msg

# Accepts 12345678-5 or 12.345.678-5 (DV may be K/k).
RUT_REGEX = re.compile(r"^(?P<body>\d{1,3}(?:\.\d{3})+|\d{1,9})-(?P<dv>[0-9kK])$")

USAGE = "Uso: <code>/codigo 12345678-5</code> o <code>/codigo 12.345.678-5</code>"


def compute_dv(body: int) -> str:
    """Compute a RUT's digito verificador (modulo 11)."""
    total, factor = 0, 2
    for digit in reversed(str(body)):
        total += int(digit) * factor
        factor = factor + 1 if factor < 7 else 2
    remainder = 11 - total % 11
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def parse_rut(text: str) -> Optional[Tuple[int, str]]:
    """Return (body, dv) if text is a well formed RUT, None otherwise."""
    match = RUT_REGEX.match(text.strip())
    if not match:
        return None
    body = int(match.group("body").replace(".", ""))
    if body == 0:
        return None
    return body, match.group("dv").upper()


async def fetch_carreras_alumnos(rut_body: int) -> List[dict]:
    """
    Query MUFASA's /carreras_alumnos. MUFASA expects the RUT without its DV.
    """
    url = mufasa.base_url.rstrip("/") + "/carreras_alumnos"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            url,
            params={"rut": str(rut_body)},
            headers={
                "Authorization": f"Bearer {mufasa.token}",
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()


@command(member_exclusive=True)
async def codigo(update: Update, context: CallbackContext, cmd: Command) -> None:
    """
    Looks up a RUT in MUFASA and replies with its carrera codes and estados
    """

    async def reply(text: str) -> None:
        await try_msg(
            context.bot,
            chat_id=update.message.chat_id,
            message_thread_id=update.message.message_thread_id,
            parse_mode="HTML",
            text=text,
            reply_to_message_id=update.message.message_id,
        )

    if not cmd.arg:
        await reply(USAGE)
        return

    rut_text = cmd.arg.strip()
    parsed = parse_rut(rut_text)
    if parsed is None:
        await reply(f"<code>{html.escape(rut_text)}</code> no es un RUT válido.\n{USAGE}")
        return

    body, dv = parsed
    expected_dv = compute_dv(body)
    if dv != expected_dv:
        await reply(
            f"El dígito verificador de <code>{html.escape(rut_text)}</code> "
            "no es válido."
        )
        return

    if not mufasa.base_url or not mufasa.token:
        logger.error("/codigo: MUFASA_BASE_URL or MUFASA_TOKEN is not set")
        await reply("MUFASA no está configurado en el bot.")
        return

    try:
        carreras = await fetch_carreras_alumnos(body)
    except httpx.HTTPStatusError as e:
        logger.error(f"/codigo: MUFASA responded HTTP {e.response.status_code}")
        await reply(f"MUFASA respondió con error HTTP {e.response.status_code}.")
        return
    except (httpx.HTTPError, ValueError) as e:
        logger.error(f"/codigo: MUFASA request failed: {type(e).__name__}: {e}")
        await reply("No se pudo consultar MUFASA.")
        return

    # MUFASA may return the same (carrera, estado) more than once.
    entries = list(
        dict.fromkeys(
            (c.get("id_carrera"), c.get("estado_texto") or "?") for c in carreras
        )
    )

    rut_display = f"{body}-{dv}"
    if not entries:
        await reply(f"No se encontraron carreras para <code>{rut_display}</code>.")
        return

    lines = [f"Carreras de <code>{rut_display}</code>:"]
    for id_carrera, estado in entries:
        lines.append(f"• <code>{id_carrera}</code>: {html.escape(str(estado))}")
    await reply("\n".join(lines))
