import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from modules.persona import buscar_persona


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


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


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("persona", persona))

    print("🤖 Brazil OSINT Bot iniciado...")
    print("Presiona Ctrl+C para detenerlo.")

    app.run_polling()


if __name__ == "__main__":
    main()
