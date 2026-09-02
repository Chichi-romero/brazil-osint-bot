import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from modules.persona import buscar_persona
from modules.empresa import buscar_empresa_por_cnpj


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

ESPERANDO_NOMBRE = 1
ESPERANDO_CNPJ = 2


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

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

    await update.message.reply_text(
        "🕵️‍♂️ BRAZIL OSINT\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "¿Qué quieres investigar?\n\n"
        "Selecciona una categoría:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ============================================================
# PERSONA
# ============================================================

async def persona(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(
            "🕵️‍♂️ Introduce el nombre completo de la persona que quieres investigar:"
        )
    else:
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

        fila_titulo = [
            InlineKeyboardButton(
                titulos.get(categoria, categoria.upper()),
                callback_data="noop",
            )
        ]

        keyboard.append(fila_titulo)

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

    await update.message.reply_text(
        f"🕵️‍♂️ PERSONA\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"Nombre:\n"
        f"{nombre}\n\n"
        f"Selecciona una fuente para realizar una búsqueda pública:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ConversationHandler.END


# ============================================================
# EMPRESA
# ============================================================

async def empresa(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🔢 CNPJ",
                callback_data="cnpj",
            )
        ],
        [
            InlineKeyboardButton(
                "🏷️ Razão Social",
                callback_data="razao_social",
            ),
            InlineKeyboardButton(
                "🏪 Nome Fantasia",
                callback_data="nome_fantasia",
            ),
        ],
    ]

    await query.message.reply_text(
        "🏢 EMPRESA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "¿Qué quieres buscar?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ============================================================
# CNPJ
# ============================================================

async def cnpj(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔢 Introduce el CNPJ que quieres investigar:\n\n"
        "Ejemplo: 12.345.678/0001-90"
    )

    return ESPERANDO_CNPJ


async def recibir_cnpj(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cnpj_usuario = update.message.text

    resultados = buscar_empresa_por_cnpj(cnpj_usuario)

    if resultados is None:

        await update.message.reply_text(
            "❌ El CNPJ no tiene un formato válido.\n\n"
            "Introduce un CNPJ de 14 dígitos.\n"
            "Ejemplo: 12.345.678/0001-90"
        )

        return ESPERANDO_CNPJ

    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 Google",
                url=resultados["google"],
            ),
            InlineKeyboardButton(
                "📰 Google News",
                url=resultados["google_news"],
            ),
        ],
        [
            InlineKeyboardButton(
                "🔎 Bing",
                url=resultados["bing"],
            ),
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=resultados["duckduckgo"],
            ),
        ],
    ]

    await update.message.reply_text(
        f"🏢 EMPRESA\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"CNPJ:\n"
        f"{resultados['cnpj']}\n\n"
        f"🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ConversationHandler.END


# ============================================================
# CANCELAR
# ============================================================

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Búsqueda cancelada."
    )

    return ConversationHandler.END


# ============================================================
# BOTONES DEL MENÚ
# ============================================================

async def botones_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    # Evita errores cuando se pulsa un botón que no necesita acción
    if query.data == "noop":
        await query.answer()
        return

    if query.data == "empresa":
        await empresa(update, context)
        return

    mensajes = {
        "razao_social":
            "🏷️ Razão Social\n\n🚧 Próximamente...",

        "nome_fantasia":
            "🏪 Nome Fantasia\n\n🚧 Próximamente...",

        "telefono":
            "📱 Módulo Teléfono\n\n🚧 Próximamente...",

        "vehiculo":
            "🚗 Módulo Vehículo\n\n🚧 Próximamente...",

        "direccion":
            "📍 Módulo Dirección\n\n🚧 Próximamente...",

        "dominio":
            "🌐 Módulo Dominio\n\n🚧 Próximamente...",
    }

    await query.answer()

    await query.message.reply_text(
        mensajes.get(
            query.data,
            "Opción no disponible."
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    app = Application.builder().token(TOKEN).build()

    # --------------------------------------------------------
    # Conversación Persona
    # --------------------------------------------------------

    conversacion_persona = ConversationHandler(

        entry_points=[
            CommandHandler("persona", persona),
            CallbackQueryHandler(
                persona,
                pattern="^persona$"
            ),
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

    # --------------------------------------------------------
    # Conversación CNPJ
    # --------------------------------------------------------

    conversacion_cnpj = ConversationHandler(

        entry_points=[
            CallbackQueryHandler(
                cnpj,
                pattern="^cnpj$"
            )
        ],

        states={
            ESPERANDO_CNPJ: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recibir_cnpj
                )
            ]
        },

        fallbacks=[
            CommandHandler("cancelar", cancelar)
        ],
    )

    # --------------------------------------------------------
    # Handlers
    # --------------------------------------------------------

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        conversacion_persona
    )

    app.add_handler(
        conversacion_cnpj
    )

    app.add_handler(
        CallbackQueryHandler(botones_menu)
    )

    # --------------------------------------------------------
    # Iniciar bot
    # --------------------------------------------------------

    print("🤖 Brazil OSINT Bot iniciado...")
    print("Presiona Ctrl+C para detenerlo.")

    app.run_polling()


if __name__ == "__main__":
    main()