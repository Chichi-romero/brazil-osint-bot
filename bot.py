import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from modules.persona import buscar_persona


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

ESPERANDO_NOMBRE = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("👤 Persona", callback_data="persona"),
            InlineKeyboardButton("🏢 Empresa", callback_data="empresa"),
        ],
        [
            InlineKeyboardButton("📱 Teléfono", callback_data="telefono"),
            InlineKeyboardButton("🚗 Vehículo", callback_data="vehiculo"),
        ],
        [
            InlineKeyboardButton("📍 Dirección", callback_data="direccion"),
            InlineKeyboardButton("🌐 Dominio", callback_data="dominio"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🕵️‍♂️ BRAZIL OSINT\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "¿Qué quieres investigar?\n\n"
        "Selecciona una categoría:",
        reply_markup=reply_markup,
    )


async def persona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕵️‍♂️ Introduce el nombre completo de la persona que quieres investigar:"
    )
    return ESPERANDO_NOMBRE


async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text

    resultados = buscar_persona(nombre)

    keyboard = []

    titulos = {
        "buscadores": "🔎 BUSCADORES",
        "redes_sociales": "📱 REDES SOCIALES",
        "profesional": "💼 PROFESIONAL",
    }

    for categoria, fuentes in resultados.items():

        keyboard.append(
            [
                InlineKeyboardButton(
                    titulos.get(categoria, categoria.upper()),
                    callback_data="info",
                )
            ]
        )

        fila = []

        for fuente in fuentes:
            fila.append(
                InlineKeyboardButton(
                    f"{fuente['emoji']} {fuente['nombre']}",
                    url=fuente["url"],
                )
            )

            if len(fila) == 2:
                keyboard.append(fila)
                fila = []

        if fila:
            keyboard.append(fila)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🕵️‍♂️ PERSONA\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"Nombre:\n"
        f"{nombre}\n\n"
        f"Selecciona una fuente para realizar una búsqueda pública:",
        reply_markup=reply_markup,
    )

    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Búsqueda cancelada."
    )
    return ConversationHandler.END


async def botones_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "persona":
        await query.message.reply_text(
            "🕵️‍♂️ Introduce el nombre completo de la persona que quieres investigar:"
        )
        return ESPERANDO_NOMBRE

    mensajes = {
        "empresa": "🏢 Módulo Empresa\n\n🚧 Próximamente...",
        "telefono": "📱 Módulo Teléfono\n\n🚧 Próximamente...",
        "vehiculo": "🚗 Módulo Vehículo\n\n🚧 Próximamente...",
        "direccion": "📍 Módulo Dirección\n\n🚧 Próximamente...",
        "dominio": "🌐 Módulo Dominio\n\n🚧 Próximamente...",
    }

    await query.message.reply_text(
        mensajes.get(query.data, "Opción no disponible.")
    )


def main():
    app = Application.builder().token(TOKEN).build()

    conversacion_persona = ConversationHandler(
        entry_points=[
            CommandHandler("persona", persona)
        ],
        states={
            ESPERANDO_NOMBRE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recibir_nombre,
                )
            ]
        },
        fallbacks=[
            CommandHandler("cancelar", cancelar)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversacion_persona)

    from telegram.ext import CallbackQueryHandler

    app.add_handler(
        CallbackQueryHandler(botones_menu)
    )

    print("🤖 Brazil OSINT Bot iniciado...")
    print("Presiona Ctrl+C para detenerlo.")

    app.run_polling()


if __name__ == "__main__":
    main()