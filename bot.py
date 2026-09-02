from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕵️‍♂️ Brazil OSINT Bot\n\n"
        "¡Bienvenido!\n"
        "Nuestro bot OSINT está funcionando. 🚀"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🤖 Brazil OSINT Bot iniciado...")
    print("Presiona Ctrl+C para detenerlo.")

    app.run_polling()


if __name__ == "__main__":
    main()
