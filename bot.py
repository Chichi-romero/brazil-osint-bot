import os
from urllib.parse import quote_plus

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
from modules.telefono import analisar_telefone
from modules.vehiculo import analisar_placa
from modules.direccion import analisar_direccion


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

ESPERANDO_NOMBRE = 1
ESPERANDO_CNPJ = 2
ESPERANDO_TELEFONO = 3
ESPERANDO_PLACA = 4
ESPERANDO_DIRECCION = 5


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

        keyboard.append([
            InlineKeyboardButton(
                titulos.get(categoria, categoria.upper()),
                callback_data="noop",
            )
        ])

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
            InlineKeyboardButton("🔢 CNPJ", callback_data="cnpj")
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
            InlineKeyboardButton("🔍 Google", url=resultados["google"]),
            InlineKeyboardButton(
                "📰 Google News",
                url=resultados["google_news"],
            ),
        ],
        [
            InlineKeyboardButton("🔎 Bing", url=resultados["bing"]),
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
# TELÉFONO
# ============================================================

async def telefono(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📱 Introduce el número de teléfono que quieres investigar:\n\n"
        "Ejemplo:\n"
        "+55 11 99999-9999"
    )

    return ESPERANDO_TELEFONO


async def recibir_telefono(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telefone_usuario = update.message.text
    resultado = analisar_telefone(telefone_usuario)

    if resultado is None:

        await update.message.reply_text(
            "❌ El número no tiene un formato válido.\n\n"
            "Introduce un teléfono brasileño válido.\n"
            "Ejemplo: +55 11 99999-9999"
        )

        return ESPERANDO_TELEFONO

    numero = resultado["numero"]
    numero_internacional = resultado["numero_internacional"]

    busqueda_numero = f'"{numero}"'
    busqueda_internacional = f'"{numero_internacional}"'

    google = (
        "https://www.google.com/search?q="
        + quote_plus(busqueda_numero)
    )

    google_internacional = (
        "https://www.google.com/search?q="
        + quote_plus(busqueda_internacional)
    )

    google_news = (
        "https://www.google.com/search?tbm=nws&q="
        + quote_plus(busqueda_numero)
    )

    bing = (
        "https://www.bing.com/search?q="
        + quote_plus(busqueda_numero)
    )

    duckduckgo = (
        "https://duckduckgo.com/?q="
        + quote_plus(busqueda_numero)
    )

    keyboard = [
        [
            InlineKeyboardButton("🔍 Google", url=google),
            InlineKeyboardButton("📰 Google News", url=google_news),
        ],
        [
            InlineKeyboardButton("🔎 Bing", url=bing),
            InlineKeyboardButton("🦆 DuckDuckGo", url=duckduckgo),
        ],
        [
            InlineKeyboardButton(
                "🌎 Google Internacional",
                url=google_internacional,
            )
        ],
    ]

    await update.message.reply_text(
        f"📱 TELÉFONO\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"📞 Número: {numero}\n"
        f"🌎 Internacional: +{numero_internacional}\n"
        f"📍 DDD: {resultado['ddd']}\n"
        f"📱 Tipo: {resultado['tipo']}\n\n"
        f"🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ConversationHandler.END


# ============================================================
# VEHÍCULO
# ============================================================

async def vehiculo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🚗 Introduce la placa del vehículo que quieres investigar:\n\n"
        "Ejemplos:\n"
        "ABC-1234\n"
        "ABC1D23"
    )

    return ESPERANDO_PLACA


async def recibir_placa(update: Update, context: ContextTypes.DEFAULT_TYPE):

    placa_usuario = update.message.text
    resultado = analisar_placa(placa_usuario)

    if resultado is None:

        await update.message.reply_text(
            "❌ La placa no tiene un formato brasileño válido.\n\n"
            "Formatos aceptados:\n"
            "• ABC-1234\n"
            "• ABC1D23"
        )

        return ESPERANDO_PLACA

    placa = resultado["placa"]
    busqueda = f'"{placa}"'

    google = (
        "https://www.google.com/search?q="
        + quote_plus(busqueda)
    )

    google_news = (
        "https://www.google.com/search?tbm=nws&q="
        + quote_plus(busqueda)
    )

    bing = (
        "https://www.bing.com/search?q="
        + quote_plus(busqueda)
    )

    duckduckgo = (
        "https://duckduckgo.com/?q="
        + quote_plus(busqueda)
    )

    keyboard = [
        [
            InlineKeyboardButton("🔍 Google", url=google),
            InlineKeyboardButton(
                "📰 Google News",
                url=google_news,
            ),
        ],
        [
            InlineKeyboardButton("🔎 Bing", url=bing),
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=duckduckgo,
            ),
        ],
    ]

    await update.message.reply_text(
        f"🚗 VEHÍCULO\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"🔢 Placa: {placa}\n"
        f"📋 Formato: {resultado['tipo']}\n\n"
        f"🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ESPERANDO_PLACA


# ============================================================
# DIRECCIÓN
# ============================================================

async def direccion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📍 Introduce la dirección que quieres investigar:\n\n"
        "Ejemplo:\n"
        "Av. Francisco Matarazzo, 1000, Água Branca, São Paulo - SP, 05001-100"
    )

    return ESPERANDO_DIRECCION


async def recibir_direccion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    direccion_usuario = update.message.text
    resultado = analisar_direccion(direccion_usuario)

    if resultado is None:

        await update.message.reply_text(
            "❌ La dirección no parece válida.\n\n"
            "Introduce una dirección más completa."
        )

        return ESPERANDO_DIRECCION

    direccion_normalizada = resultado["direccion"]
    cep = resultado["cep"]

    busqueda_direccion = f'"{direccion_normalizada}"'

    google = (
        "https://www.google.com/search?q="
        + quote_plus(busqueda_direccion)
    )

    google_maps = (
        "https://www.google.com/maps/search/?api=1&query="
        + quote_plus(direccion_normalizada)
    )

    google_news = (
        "https://www.google.com/search?tbm=nws&q="
        + quote_plus(busqueda_direccion)
    )

    bing = (
        "https://www.bing.com/search?q="
        + quote_plus(busqueda_direccion)
    )

    duckduckgo = (
        "https://duckduckgo.com/?q="
        + quote_plus(busqueda_direccion)
    )

    keyboard = [
        [
            InlineKeyboardButton("🔍 Google", url=google),
            InlineKeyboardButton("🗺️ Google Maps", url=google_maps),
        ],
        [
            InlineKeyboardButton("📰 Google News", url=google_news),
            InlineKeyboardButton("🔎 Bing", url=bing),
        ],
        [
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=duckduckgo,
            )
        ],
    ]

    cep_texto = cep if cep else "No detectado"

    await update.message.reply_text(
        f"📍 DIRECCIÓN\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"🏠 Dirección:\n"
        f"{direccion_normalizada}\n\n"
        f"📮 CEP: {cep_texto}\n\n"
        f"🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ESPERANDO_DIRECCION


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

    conversacion_telefono = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                telefono,
                pattern="^telefono$"
            )
        ],
        states={
            ESPERANDO_TELEFONO: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recibir_telefono
                )
            ]
        },
        fallbacks=[
            CommandHandler("cancelar", cancelar)
        ],
    )

    conversacion_vehiculo = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                vehiculo,
                pattern="^vehiculo$"
            )
        ],
        states={
            ESPERANDO_PLACA: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recibir_placa
                )
            ]
        },
        fallbacks=[
            CommandHandler("cancelar", cancelar)
        ],
    )

    conversacion_direccion = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                direccion,
                pattern="^direccion$"
            )
        ],
        states={
            ESPERANDO_DIRECCION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recibir_direccion
                )
            ]
        },
        fallbacks=[
            CommandHandler("cancelar", cancelar)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversacion_persona)
    app.add_handler(conversacion_cnpj)
    app.add_handler(conversacion_telefono)
    app.add_handler(conversacion_vehiculo)
    app.add_handler(conversacion_direccion)
    app.add_handler(CallbackQueryHandler(botones_menu))

    print("🤖 Brazil OSINT Bot iniciado...")
    print("Presiona Ctrl+C para detenerlo.")

    app.run_polling()


if __name__ == "__main__":
    main()