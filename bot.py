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
from modules.dominio import analisar_dominio


# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


# ============================================================
# ESTADOS
# ============================================================

ESPERANDO_NOMBRE = 1
ESPERANDO_CNPJ = 2
ESPERANDO_TELEFONO = 3
ESPERANDO_PLACA = 4
ESPERANDO_DIRECCION = 5
ESPERANDO_DOMINIO = 6


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def teclado_menu_principal():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "👤 Persona",
                callback_data="persona"
            ),
            InlineKeyboardButton(
                "🏢 Empresa",
                callback_data="empresa"
            ),
        ],
        [
            InlineKeyboardButton(
                "📱 Teléfono",
                callback_data="telefono"
            ),
            InlineKeyboardButton(
                "🚗 Vehículo",
                callback_data="vehiculo"
            ),
        ],
        [
            InlineKeyboardButton(
                "📍 Dirección",
                callback_data="direccion"
            ),
            InlineKeyboardButton(
                "🌐 Dominio",
                callback_data="dominio"
            ),
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.callback_query:

        query = update.callback_query
        await query.answer()

        await query.message.reply_text(
            "🕵️‍♂️ BRAZIL OSINT\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "¿Qué quieres investigar?\n\n"
            "Selecciona una categoría:",
            reply_markup=teclado_menu_principal(),
        )

    else:

        await update.message.reply_text(
            "🕵️‍♂️ BRAZIL OSINT\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "¿Qué quieres investigar?\n\n"
            "Selecciona una categoría:",
            reply_markup=teclado_menu_principal(),
        )


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

async def menu_principal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🕵️‍♂️ BRAZIL OSINT\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "¿Qué quieres investigar?\n\n"
        "Selecciona una categoría:",
        reply_markup=teclado_menu_principal(),
    )

    return ConversationHandler.END


# ============================================================
# BOTONES DE RESULTADO
# ============================================================

def teclado_busqueda():
    return [
        [
            InlineKeyboardButton(
                "🔁 Nueva búsqueda",
                callback_data="nueva_busqueda"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Menú principal",
                callback_data="menu_principal"
            )
        ],
    ]


# ============================================================
# PERSONA
# ============================================================

async def persona(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.callback_query:

        query = update.callback_query
        await query.answer()

        await query.message.reply_text(
            "🕵️‍♂️ PERSONA\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "Introduce el nombre completo de la persona:"
        )

    else:

        await update.message.reply_text(
            "🕵️‍♂️ PERSONA\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "Introduce el nombre completo de la persona:"
        )

    return ESPERANDO_NOMBRE


async def recibir_nombre(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    nombre = update.message.text.strip()

    if not nombre:

        await update.message.reply_text(
            "❌ Introduce un nombre válido."
        )

        return ESPERANDO_NOMBRE

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
                titulos.get(
                    categoria,
                    categoria.upper()
                ),
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

    keyboard.extend(teclado_busqueda())

    await update.message.reply_text(
        "🕵️‍♂️ PERSONA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"👤 Nombre:\n"
        f"{nombre}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ESPERANDO_NOMBRE


async def nueva_busqueda_persona(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔁 PERSONA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce el nombre completo de la nueva persona:"
    )

    return ESPERANDO_NOMBRE


# ============================================================
# EMPRESA
# ============================================================

async def empresa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🔢 CNPJ",
                callback_data="cnpj"
            )
        ],
        [
            InlineKeyboardButton(
                "🏷️ Razão Social",
                callback_data="razao_social"
            ),
            InlineKeyboardButton(
                "🏪 Nome Fantasia",
                callback_data="nome_fantasia"
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

async def cnpj(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔢 Introduce el CNPJ que quieres investigar:\n\n"
        "Ejemplo:\n"
        "12.345.678/0001-90"
    )

    return ESPERANDO_CNPJ


async def recibir_cnpj(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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
                url=resultados["google"]
            ),
            InlineKeyboardButton(
                "📰 Google News",
                url=resultados["google_news"]
            ),
        ],
        [
            InlineKeyboardButton(
                "🔎 Bing",
                url=resultados["bing"]
            ),
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=resultados["duckduckgo"]
            ),
        ],
    ]

    keyboard.extend(teclado_busqueda())

    await update.message.reply_text(
        "🏢 EMPRESA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🔢 CNPJ:\n"
        f"{resultados['cnpj']}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ESPERANDO_CNPJ


async def nueva_busqueda_cnpj(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔁 CNPJ\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce el nuevo CNPJ:"
    )

    return ESPERANDO_CNPJ


# ============================================================
# TELÉFONO
# ============================================================

async def telefono(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📱 Introduce el número de teléfono que quieres investigar:\n\n"
        "Ejemplo:\n"
        "+55 11 99999-9999"
    )

    return ESPERANDO_TELEFONO


async def recibir_telefono(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    telefone_usuario = update.message.text

    resultado = analisar_telefone(telefone_usuario)

    if resultado is None:

        await update.message.reply_text(
            "❌ El número no tiene un formato válido.\n\n"
            "Introduce un teléfono brasileño válido.\n"
            "Ejemplo:\n"
            "+55 11 99999-9999"
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
            InlineKeyboardButton(
                "🔍 Google",
                url=google
            ),
            InlineKeyboardButton(
                "📰 Google News",
                url=google_news
            ),
        ],
        [
            InlineKeyboardButton(
                "🔎 Bing",
                url=bing
            ),
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=duckduckgo
            ),
        ],
        [
            InlineKeyboardButton(
                "🌎 Google Internacional",
                url=google_internacional
            ),
        ],
    ]

    keyboard.extend(teclado_busqueda())

    await update.message.reply_text(
        "📱 TELÉFONO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"📞 Número: {numero}\n"
        f"🌎 Internacional: +{numero_internacional}\n"
        f"📍 DDD: {resultado['ddd']}\n"
        f"📱 Tipo: {resultado['tipo']}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ESPERANDO_TELEFONO


async def nueva_busqueda_telefono(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔁 TELÉFONO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce el nuevo número:"
    )

    return ESPERANDO_TELEFONO


# ============================================================
# VEHÍCULO
# ============================================================

async def vehiculo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🚗 Introduce la placa del vehículo:\n\n"
        "Ejemplos:\n"
        "ABC-1234\n"
        "ABC1D23"
    )

    return ESPERANDO_PLACA


async def recibir_placa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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
            InlineKeyboardButton(
                "🔍 Google",
                url=google
            ),
            InlineKeyboardButton(
                "📰 Google News",
                url=google_news
            ),
        ],
        [
            InlineKeyboardButton(
                "🔎 Bing",
                url=bing
            ),
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=duckduckgo
            ),
        ],
    ]

    keyboard.extend(teclado_busqueda())

    await update.message.reply_text(
        "🚗 VEHÍCULO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🔢 Placa: {placa}\n"
        f"📋 Formato: {resultado['tipo']}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ESPERANDO_PLACA


async def nueva_busqueda_vehiculo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔁 VEHÍCULO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce la nueva placa:"
    )

    return ESPERANDO_PLACA


# ============================================================
# DIRECCIÓN
# ============================================================

async def direccion(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📍 DIRECCIÓN\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce una dirección o un CEP.\n\n"
        "Ejemplos:\n"
        "Av. Francisco Matarazzo, 1000, São Paulo - SP\n"
        "05001-100"
    )

    return ESPERANDO_DIRECCION


async def recibir_direccion(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    direccion_usuario = update.message.text

    resultado = analisar_direccion(direccion_usuario)

    if resultado is None:

        await update.message.reply_text(
            "❌ El dato no parece válido.\n\n"
            "Introduce una dirección o un CEP válido."
        )

        return ESPERANDO_DIRECCION

    direccion_normalizada = resultado["direccion"]
    cep = resultado["cep"]
    datos_cep = resultado["datos_cep"]
    datos_geo = resultado.get("datos_geocodificacion")
    cep_confirmado = resultado.get("cep_confirmado", False)

    # ========================================================
    # CASO 1: CEP INTRODUCIDO DIRECTAMENTE
    # ========================================================

    if resultado["es_cep"]:

        if datos_cep is None:

            await update.message.reply_text(
                "❌ No encontramos información para ese CEP.\n\n"
                "Comprueba que el CEP tenga 8 dígitos."
            )

            return ESPERANDO_DIRECCION

        logradouro = datos_cep.get(
            "logradouro",
            "No informado"
        )

        bairro = datos_cep.get(
            "bairro",
            "No informado"
        )

        cidade = datos_cep.get(
            "cidade",
            "No informado"
        )

        uf = datos_cep.get(
            "uf",
            "No informado"
        )

        estado = datos_cep.get(
            "estado",
            "No informado"
        )

        regiao = datos_cep.get(
            "regiao",
            "No informado"
        )

        ddd = datos_cep.get(
            "ddd",
            "No informado"
        )

        ibge = datos_cep.get(
            "ibge",
            "No informado"
        )

        consulta = (
            f'"{logradouro}" "{bairro}" '
            f'"{cidade}" "{uf}"'
        )

        google = (
            "https://www.google.com/search?q="
            + quote_plus(consulta)
        )

        google_maps = (
            "https://www.google.com/maps/search/?api=1&query="
            + quote_plus(
                f"{logradouro}, {bairro}, "
                f"{cidade} - {uf}"
            )
        )

        google_news = (
            "https://www.google.com/search?tbm=nws&q="
            + quote_plus(consulta)
        )

        bing = (
            "https://www.bing.com/search?q="
            + quote_plus(consulta)
        )

        duckduckgo = (
            "https://duckduckgo.com/?q="
            + quote_plus(consulta)
        )

        correios = (
            "https://buscacepinter.correios.com.br/"
            "app/endereco/index.php"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔍 Google",
                    url=google
                ),
                InlineKeyboardButton(
                    "🗺️ Google Maps",
                    url=google_maps
                ),
            ],
            [
                InlineKeyboardButton(
                    "📰 Google News",
                    url=google_news
                ),
                InlineKeyboardButton(
                    "🔎 Bing",
                    url=bing
                ),
            ],
            [
                InlineKeyboardButton(
                    "🦆 DuckDuckGo",
                    url=duckduckgo
                ),
            ],
            [
                InlineKeyboardButton(
                    "📮 Ver Correios",
                    url=correios
                ),
            ],
        ]

        keyboard.extend(teclado_busqueda())

        await update.message.reply_text(
            "📮 CEP\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"📮 CEP: {datos_cep.get('cep', direccion_normalizada)}\n"
            "✅ Confirmado por ViaCEP\n\n"
            f"🏠 Logradouro: {logradouro}\n"
            f"🏘️ Bairro: {bairro}\n"
            f"🏙️ Ciudad: {cidade}\n"
            f"🇧🇷 Estado: {estado} ({uf})\n"
            f"🌎 Región: {regiao}\n"
            f"📞 DDD: {ddd}\n"
            f"🔢 IBGE: {ibge}\n\n"
            "🔎 Búsquedas públicas:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return ESPERANDO_DIRECCION

    # ========================================================
    # CASO 2: DIRECCIÓN
    # ========================================================

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

    osm_url = (
        "https://www.openstreetmap.org/search?query="
        + quote_plus(direccion_normalizada)
    )

    correios = (
        "https://buscacepinter.correios.com.br/"
        "app/localidade_logradouro/index.php"
    )

    # ========================================================
    # INFORMACIÓN DE GEOCODIFICACIÓN
    # ========================================================

    geo_extra = ""

    if datos_geo:

        display_name = datos_geo.get(
            "display_name",
            "No disponible"
        )

        latitude = datos_geo.get(
            "latitude",
            "No disponible"
        )

        longitude = datos_geo.get(
            "longitude",
            "No disponible"
        )

        geo_logradouro = datos_geo.get(
            "logradouro"
        )

        geo_numero = datos_geo.get(
            "numero"
        )

        geo_bairro = datos_geo.get(
            "bairro"
        )

        geo_cidade = datos_geo.get(
            "cidade"
        )

        geo_estado = datos_geo.get(
            "estado"
        )

        geo_cep_sugerido = datos_geo.get(
            "cep_sugerido"
        )

        geo_extra = (
            "🗺️ GEOCODIFICACIÓN\n"
            "━━━━━━━━━━━━━━━━\n"
            f"📌 Ubicación: {display_name}\n"
            f"🌐 Latitud: {latitude}\n"
            f"🌐 Longitud: {longitude}\n"
        )

        if geo_logradouro:
            geo_extra += (
                f"🏠 Logradouro: {geo_logradouro}\n"
            )

        if geo_numero:
            geo_extra += (
                f"🔢 Número: {geo_numero}\n"
            )

        if geo_bairro:
            geo_extra += (
                f"🏘️ Bairro: {geo_bairro}\n"
            )

        if geo_cidade:
            geo_extra += (
                f"🏙️ Ciudad: {geo_cidade}\n"
            )

        if geo_estado:
            geo_extra += (
                f"🇧🇷 Estado: {geo_estado}\n"
            )

        if geo_cep_sugerido and not cep_confirmado:
            geo_extra += (
                f"📮 CEP sugerido: {geo_cep_sugerido}\n"
                "⚠️ No verificado\n"
            )

    # ========================================================
    # INFORMACIÓN DEL CEP
    # ========================================================

    if cep and cep_confirmado and datos_cep:

        logradouro = datos_cep.get(
            "logradouro",
            "No informado"
        )

        bairro = datos_cep.get(
            "bairro",
            "No informado"
        )

        cidade = datos_cep.get(
            "cidade",
            "No informado"
        )

        uf = datos_cep.get(
            "uf",
            "No informado"
        )

        estado = datos_cep.get(
            "estado",
            "No informado"
        )

        regiao = datos_cep.get(
            "regiao",
            "No informado"
        )

        ddd = datos_cep.get(
            "ddd",
            "No informado"
        )

        ibge = datos_cep.get(
            "ibge",
            "No informado"
        )

        info_extra = (
            "📮 INFORMACIÓN DEL CEP\n"
            "━━━━━━━━━━━━━━━━\n"
            f"📮 CEP: {datos_cep.get('cep', cep)}\n"
            "✅ Confirmado por ViaCEP\n"
            f"🏠 Logradouro: {logradouro}\n"
            f"🏘️ Bairro: {bairro}\n"
            f"🏙️ Ciudad: {cidade}\n"
            f"🇧🇷 Estado: {estado} ({uf})\n"
            f"🌎 Región: {regiao}\n"
            f"📞 DDD: {ddd}\n"
            f"🔢 IBGE: {ibge}\n"
        )

    elif cep:

        info_extra = (
            "📮 CEP SUGERIDO\n"
            "━━━━━━━━━━━━━━━━\n"
            f"📮 CEP: {cep}\n"
            "⚠️ Encontrado por geocodificación.\n"
            "⚠️ No confirmado por ViaCEP.\n"
        )

    else:

        info_extra = (
            "📮 CEP\n"
            "━━━━━━━━━━━━━━━━\n"
            "📮 CEP: No encontrado automáticamente\n"
        )

    # ========================================================
    # TECLADO
    # ========================================================

    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 Google",
                url=google
            ),
            InlineKeyboardButton(
                "🗺️ Google Maps",
                url=google_maps
            ),
        ],
        [
            InlineKeyboardButton(
                "📰 Google News",
                url=google_news
            ),
            InlineKeyboardButton(
                "🔎 Bing",
                url=bing
            ),
        ],
        [
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=duckduckgo
            ),
            InlineKeyboardButton(
                "🌍 OpenStreetMap",
                url=osm_url
            ),
        ],
        [
            InlineKeyboardButton(
                "📮 Ver en Correios",
                url=correios
            ),
        ],
    ]

    keyboard.extend(teclado_busqueda())

    await update.message.reply_text(
        "📍 DIRECCIÓN\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🏠 Dirección:\n"
        f"{direccion_normalizada}\n\n"
        f"{info_extra}\n"
        f"{geo_extra}\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ESPERANDO_DIRECCION


async def nueva_busqueda_direccion(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔁 DIRECCIÓN\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce la nueva dirección o CEP:"
    )

    return ESPERANDO_DIRECCION


# ============================================================
# DOMINIO
# ============================================================

async def dominio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🌐 DOMINIO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce el dominio que quieres investigar:\n\n"
        "Ejemplos:\n"
        "google.com\n"
        "empresa.com.br\n"
        "https://www.empresa.com.br"
    )

    return ESPERANDO_DOMINIO


async def recibir_dominio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    dominio_usuario = update.message.text

    resultado = analisar_dominio(dominio_usuario)

    if resultado is None:

        await update.message.reply_text(
            "❌ El dominio no tiene un formato válido.\n\n"
            "Ejemplos:\n"
            "google.com\n"
            "empresa.com.br"
        )

        return ESPERANDO_DOMINIO

    dominio = resultado["dominio"]
    tld = resultado["tld"]
    subdominio = resultado["subdominio"]

    busqueda = f'"{dominio}"'

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

    google_site = (
        "https://www.google.com/search?q="
        + quote_plus(
            f"site:{dominio}"
        )
    )

    google_maps = (
        "https://www.google.com/maps/search/?api=1&query="
        + quote_plus(dominio)
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 Google",
                url=google
            ),
            InlineKeyboardButton(
                "📰 Google News",
                url=google_news
            ),
        ],
        [
            InlineKeyboardButton(
                "🔎 Bing",
                url=bing
            ),
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=duckduckgo
            ),
        ],
        [
            InlineKeyboardButton(
                "🌐 Buscar dentro del dominio",
                url=google_site
            )
        ],
        [
            InlineKeyboardButton(
                "🗺️ Google Maps",
                url=google_maps
            )
        ],
    ]

    keyboard.extend(teclado_busqueda())

    subdominio_texto = (
        subdominio
        if subdominio
        else "No detectado"
    )

    await update.message.reply_text(
        "🌐 DOMINIO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🌐 Dominio: {dominio}\n"
        f"🔤 TLD: .{tld}\n"
        f"🔗 Subdominio: {subdominio_texto}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ESPERANDO_DOMINIO


async def nueva_busqueda_dominio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🔁 DOMINIO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce el nuevo dominio:"
    )

    return ESPERANDO_DOMINIO


# ============================================================
# CANCELAR
# ============================================================

async def cancelar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "❌ Búsqueda cancelada.\n\n"
        "Usa /start para volver al menú principal."
    )

    return ConversationHandler.END


# ============================================================
# BOTONES GENERALES
# ============================================================

async def botones_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if query.data == "noop":

        await query.answer()
        return

    if query.data == "empresa":

        await empresa(update, context)
        return

    await query.answer()

    mensajes = {
        "razao_social":
            "🏷️ Razão Social\n\n🚧 Próximamente...",

        "nome_fantasia":
            "🏪 Nome Fantasia\n\n🚧 Próximamente...",
    }

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

    if not TOKEN:
        raise RuntimeError(
            "❌ BOT_TOKEN no está configurado en el archivo .env"
        )

    app = Application.builder().token(TOKEN).build()

    # ========================================================
    # PERSONA
    # ========================================================

    conversacion_persona = ConversationHandler(
        entry_points=[
            CommandHandler(
                "persona",
                persona
            ),
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
            CommandHandler(
                "cancelar",
                cancelar
            ),
            CallbackQueryHandler(
                nueva_busqueda_persona,
                pattern="^nueva_busqueda$"
            ),
            CallbackQueryHandler(
                menu_principal,
                pattern="^menu_principal$"
            ),
        ],

        allow_reentry=True,
    )

    # ========================================================
    # CNPJ
    # ========================================================

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
            CommandHandler(
                "cancelar",
                cancelar
            ),
            CallbackQueryHandler(
                nueva_busqueda_cnpj,
                pattern="^nueva_busqueda$"
            ),
            CallbackQueryHandler(
                menu_principal,
                pattern="^menu_principal$"
            ),
        ],

        allow_reentry=True,
    )

    # ========================================================
    # TELÉFONO
    # ========================================================

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
            CommandHandler(
                "cancelar",
                cancelar
            ),
            CallbackQueryHandler(
                nueva_busqueda_telefono,
                pattern="^nueva_busqueda$"
            ),
            CallbackQueryHandler(
                menu_principal,
                pattern="^menu_principal$"
            ),
        ],

        allow_reentry=True,
    )

    # ========================================================
    # VEHÍCULO
    # ========================================================

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
            CommandHandler(
                "cancelar",
                cancelar
            ),
            CallbackQueryHandler(
                nueva_busqueda_vehiculo,
                pattern="^nueva_busqueda$"
            ),
            CallbackQueryHandler(
                menu_principal,
                pattern="^menu_principal$"
            ),
        ],

        allow_reentry=True,
    )

    # ========================================================
    # DIRECCIÓN
    # ========================================================

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
            CommandHandler(
                "cancelar",
                cancelar
            ),
            CallbackQueryHandler(
                nueva_busqueda_direccion,
                pattern="^nueva_busqueda$"
            ),
            CallbackQueryHandler(
                menu_principal,
                pattern="^menu_principal$"
            ),
        ],

        allow_reentry=True,
    )

    # ========================================================
    # DOMINIO
    # ========================================================

    conversacion_dominio = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                dominio,
                pattern="^dominio$"
            )
        ],

        states={
            ESPERANDO_DOMINIO: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    recibir_dominio
                )
            ]
        },

        fallbacks=[
            CommandHandler(
                "cancelar",
                cancelar
            ),
            CallbackQueryHandler(
                nueva_busqueda_dominio,
                pattern="^nueva_busqueda$"
            ),
            CallbackQueryHandler(
                menu_principal,
                pattern="^menu_principal$"
            ),
        ],

        allow_reentry=True,
    )

    # ========================================================
    # HANDLERS
    # ========================================================

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        conversacion_persona
    )

    app.add_handler(
        conversacion_cnpj
    )

    app.add_handler(
        conversacion_telefono
    )

    app.add_handler(
        conversacion_vehiculo
    )

    app.add_handler(
        conversacion_direccion
    )

    app.add_handler(
        conversacion_dominio
    )

    app.add_handler(
        CallbackQueryHandler(
            botones_menu
        )
    )

    print("🤖 Brazil OSINT Bot iniciado...")
    print("Presiona Ctrl+C para detenerlo.")

    app.run_polling()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()