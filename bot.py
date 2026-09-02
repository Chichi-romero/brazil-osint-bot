import os
from dotenv import load_dotenv

from telegram import Update
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
    await update.message.reply_text(
        "🕵️‍♂️ Brazil OSINT Bot\n\n"
        "¡Bienvenido!\n"
        "Nuestro bot OSINT está funcionando. 🚀\n\n"
        "Usa /persona para comenzar una búsqueda."
    )


async def persona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕵️‍♂️ Introduce el nombre completo de la persona que quieres investigar:"
    )
    return ESPERANDO_NOMBRE


async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text

    resultado = buscar_persona(nombre)

    await update.message.reply_text(
        f"🔎 Resultado:\n\n{resultado}"
    )

    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Búsqueda cancelada."
    )
    return ConversationHandler.END


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
                    recibir_nombre
                )
            ]
        },
        fallbacks=[
            CommandHandler("cancelar", cancelar)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversacion_persona)

    print("🤖 Brazil OSINT Bot iniciado...")
    print("Presiona Ctrl+C para detenerlo.")

    app.run_polling()


if __name__ == "__main__":
    main()