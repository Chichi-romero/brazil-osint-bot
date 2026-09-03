import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

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
from modules.empresa import (
    buscar_empresa_por_cnpj,
    buscar_empresa_por_nome,
)
from modules.telefono import analisar_telefone
from modules.vehiculo import analisar_placa
from modules.direccion import analisar_direccion
from modules.dominio import analisar_dominio


# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()

TOKEN = os.getenv(
    "BOT_TOKEN"
)


# ============================================================
# ESTADOS
# ============================================================

ESPERANDO_NOMBRE = 1
ESPERANDO_CNPJ = 2
ESPERANDO_TELEFONO = 3
ESPERANDO_PLACA = 4
ESPERANDO_DIRECCION = 5
ESPERANDO_DOMINIO = 6
ESPERANDO_RAZAO_SOCIAL = 7
ESPERANDO_NOME_FANTASIA = 8


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


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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
            "Introduce el nombre completo "
            "de la persona:"
        )

    else:

        await update.message.reply_text(
            "🕵️‍♂️ PERSONA\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "Introduce el nombre completo "
            "de la persona:"
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

    resultados = buscar_persona(
        nombre
    )

    keyboard = []

    titulos = {
        "buscadores":
            "🔎 BUSCADORES",

        "redes_sociales":
            "📱 REDES SOCIALES",

        "profesional":
            "💼 PROFESIONAL",
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
                    f"{fuente['emoji']} "
                    f"{fuente['nombre']}",
                    url=fuente["url"],
                )
            )

            if len(fila) == 2:

                keyboard.append(fila)

                fila = []

        if fila:

            keyboard.append(
                fila
            )

    keyboard.extend(
        teclado_busqueda()
    )

    await update.message.reply_text(
        "🕵️‍♂️ PERSONA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"👤 Nombre:\n"
        f"{nombre}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
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
        "Introduce el nombre completo "
        "de la nueva persona:"
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
            )
        ],
        [
            InlineKeyboardButton(
                "🏪 Nome Fantasia",
                callback_data="nome_fantasia"
            )
        ],
    ]

    await query.message.reply_text(
        "🏢 EMPRESA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "¿Qué quieres buscar?",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
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
        "🔢 Introduce el CNPJ que quieres "
        "investigar:\n\n"
        "Ejemplo:\n"
        "00.000.000/0001-91"
    )

    return ESPERANDO_CNPJ


async def recibir_cnpj(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    cnpj_usuario = update.message.text

    resultado = buscar_empresa_por_cnpj(
        cnpj_usuario
    )

    if resultado is None:

        await update.message.reply_text(
            "❌ El CNPJ no tiene un formato válido "
            "o no encontramos datos públicos.\n\n"
            "Introduce un CNPJ válido de 14 caracteres."
        )

        return ESPERANDO_CNPJ

    dados = resultado.get(
        "dados",
        {}
    )

    identificacao = dados.get(
        "identificacao",
        {}
    )

    status = dados.get(
        "status",
        {}
    )

    atividades = dados.get(
        "atividades",
        {}
    )

    localizacao = dados.get(
        "localizacao",
        {}
    )

    contato = dados.get(
        "contato",
        {}
    )

    financas = dados.get(
        "financas",
        {}
    )

    quadro = dados.get(
        "quadro_societario",
        []
    )

    context.user_data[
        "empresa_cnpj"
    ] = resultado["cnpj"]

    context.user_data[
        "empresa_dados"
    ] = dados

    context.user_data[
        "qsa"
    ] = quadro

    context.user_data[
        "qsa_pagina"
    ] = 0

    razao_social = identificacao.get(
        "razao_social",
        "No informado"
    )

    nome_fantasia = identificacao.get(
        "nome_fantasia",
        "No informado"
    )

    tipo = identificacao.get(
        "tipo",
        "No informado"
    )

    data_abertura = identificacao.get(
        "data_abertura",
        "No informado"
    )

    situacao = status.get(
        "situacao",
        "No informado"
    )

    data_situacao = status.get(
        "data",
        "No informado"
    )

    motivo = status.get(
        "motivo",
        "No informado"
    )

    cnae = atividades.get(
        "cnae_fiscal",
        "No informado"
    )

    cnae_descricao = atividades.get(
        "cnae_descricao",
        "No informado"
    )

    tipo_logradouro = localizacao.get(
        "tipo_logradouro",
        ""
    )

    logradouro = localizacao.get(
        "logradouro",
        ""
    )

    numero = localizacao.get(
        "numero",
        ""
    )

    complemento = localizacao.get(
        "complemento",
        ""
    )

    bairro = localizacao.get(
        "bairro",
        ""
    )

    cep = localizacao.get(
        "cep",
        ""
    )

    municipio = localizacao.get(
        "municipio",
        ""
    )

    uf = localizacao.get(
        "uf",
        ""
    )

    ddd = contato.get(
        "ddd",
        ""
    )

    telefone = contato.get(
        "telefone",
        ""
    )

    email = contato.get(
        "email",
        ""
    )

    capital_social = financas.get(
        "capital_social"
    )

    porte = financas.get(
        "porte",
        "No informado"
    )

    if isinstance(
        capital_social,
        (int, float)
    ):

        capital_formatado = (
            f"R$ {capital_social:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    else:

        capital_formatado = (
            "No informado"
        )

    cep_numerico = "".join(
        c for c in str(cep)
        if c.isdigit()
    )

    if len(cep_numerico) == 8:

        cep_formatado = (
            f"{cep_numerico[:5]}-"
            f"{cep_numerico[5:]}"
        )

    else:

        cep_formatado = (
            str(cep)
            if cep
            else "No informado"
        )

    telefone_numerico = "".join(
        c for c in str(telefone)
        if c.isdigit()
    )

    if (
        ddd
        and len(telefone_numerico)
        in (8, 9)
    ):

        telefone_formatado = (
            f"({ddd}) "
            f"{telefone_numerico[:4]}-"
            f"{telefone_numerico[4:]}"
        )

    elif telefone:

        telefone_formatado = (
            f"({ddd}) {telefone}"
            if ddd
            else str(telefone)
        )

    else:

        telefone_formatado = (
            "No informado"
        )

    endereco_partes = []

    if tipo_logradouro:

        endereco_partes.append(
            tipo_logradouro
        )

    if logradouro:

        endereco_partes.append(
            logradouro
        )

    endereco_linha = " ".join(
        endereco_partes
    )

    if numero:

        endereco_linha += (
            f", {numero}"
        )

    if not endereco_linha:

        endereco_linha = (
            "No informado"
        )

    consulta = (
        f'"{razao_social}" '
        f'"{resultado["cnpj"]}"'
    )

    google = (
        "https://www.google.com/search?q="
        + quote_plus(consulta)
    )

    google_news = (
        "https://www.google.com/search?"
        "tbm=nws&q="
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

    google_maps = (
        "https://www.google.com/maps/search/"
        "?api=1&query="
        + quote_plus(
            f"{endereco_linha}, "
            f"{bairro}, "
            f"{municipio} - {uf}"
        )
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
                "🗺️ Google Maps",
                url=google_maps
            ),
        ],
    ]

    if quadro:

        keyboard.append([
            InlineKeyboardButton(
                f"👥 Ver QSA ({len(quadro)})",
                callback_data="qsa_ver"
            )
        ])

    keyboard.extend(
        teclado_busqueda()
    )

    mensagem = (
        "🏢 EMPRESA\n"
        "━━━━━━━━━━━━━━━━\n\n"

        f"🔢 CNPJ:\n"
        f"{resultado['cnpj_formatado']}\n\n"

        "🏛️ IDENTIFICACIÓN\n"
        "━━━━━━━━━━━━━━━━\n"
        f"🏢 Razão Social: "
        f"{razao_social}\n"
        f"🏷️ Nome Fantasia: "
        f"{nome_fantasia}\n"
        f"🏢 Tipo: {tipo}\n"
        f"📅 Abertura: "
        f"{data_abertura}\n\n"

        "📊 SITUAÇÃO\n"
        "━━━━━━━━━━━━━━━━\n"
        f"🟢 Situação: "
        f"{situacao}\n"
        f"📅 Data: "
        f"{data_situacao}\n"
        f"ℹ️ Motivo: "
        f"{motivo}\n\n"

        "💼 ATIVIDADE\n"
        "━━━━━━━━━━━━━━━━\n"
        f"🔢 CNAE: {cnae}\n"
        f"📋 {cnae_descricao}\n\n"

        "📍 LOCALIZAÇÃO\n"
        "━━━━━━━━━━━━━━━━\n"
        f"🏠 {endereco_linha}\n"
        f"🏘️ Bairro: {bairro}\n"
        f"📮 CEP: {cep_formatado}\n"
        f"🏙️ Cidade: {municipio}\n"
        f"🇧🇷 UF: {uf}\n\n"

        "📞 CONTACTO\n"
        "━━━━━━━━━━━━━━━━\n"
        f"📞 DDD: {ddd}\n"
        f"☎️ Telefone: "
        f"{telefone_formatado}\n"
        f"📧 E-mail: {email}\n\n"

        "💰 FINANZAS\n"
        "━━━━━━━━━━━━━━━━\n"
        f"💵 Capital Social: "
        f"{capital_formatado}\n"
        f"🏷️ Porte: {porte}\n\n"
    )

    if quadro:

        mensagem += (
            "👥 QUADRO SOCIETÁRIO\n"
            "━━━━━━━━━━━━━━━━\n"
            f"👥 Total de registros: "
            f"{len(quadro)}\n"
            "👉 Pulsa «Ver QSA» "
            "para consultar todos.\n\n"
        )

    else:

        mensagem += (
            "👥 QUADRO SOCIETÁRIO\n"
            "━━━━━━━━━━━━━━━━\n"
            "No informado.\n\n"
        )

    mensagem += (
        "🔎 Búsquedas públicas:"
    )

    await update.message.reply_text(
        mensagem,
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
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
# QSA
# ============================================================

TAMANHO_PAGINA_QSA = 10


def teclado_qsa(
    pagina,
    total
):

    total_paginas = (
        (
            total
            + TAMANHO_PAGINA_QSA
            - 1
        )
        // TAMANHO_PAGINA_QSA
    )

    keyboard = []

    navegacion = []

    if pagina > 0:

        navegacion.append(
            InlineKeyboardButton(
                "⬅️ Anteriores",
                callback_data="qsa_prev"
            )
        )

    if pagina < total_paginas - 1:

        navegacion.append(
            InlineKeyboardButton(
                "Siguientes ➡️",
                callback_data="qsa_next"
            )
        )

    if navegacion:

        keyboard.append(
            navegacion
        )

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Volver a Empresa",
            callback_data="qsa_volver"
        )
    ])

    return keyboard


async def mostrar_qsa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    qsa = context.user_data.get(
        "qsa",
        []
    )

    pagina = context.user_data.get(
        "qsa_pagina",
        0
    )

    if not qsa:

        await query.message.reply_text(
            "❌ No hay registros de QSA disponibles."
        )

        return ESPERANDO_CNPJ

    total = len(qsa)

    inicio = (
        pagina
        * TAMANHO_PAGINA_QSA
    )

    fim = min(
        inicio + TAMANHO_PAGINA_QSA,
        total
    )

    registros = qsa[
        inicio:fim
    ]

    total_paginas = (
        (
            total
            + TAMANHO_PAGINA_QSA
            - 1
        )
        // TAMANHO_PAGINA_QSA
    )

    mensagem = (
        "👥 QUADRO SOCIETÁRIO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"📄 Registros "
        f"{inicio + 1}–{fim} de {total}\n"
        f"📑 Página "
        f"{pagina + 1} de {total_paginas}\n\n"
    )

    for numero, pessoa in enumerate(
        registros,
        start=inicio + 1
    ):

        nome = pessoa.get(
            "nome",
            "No informado"
        )

        qualificacao = pessoa.get(
            "qualificacao",
            "No informada"
        )

        data_entrada = pessoa.get(
            "data_entrada"
        )

        mensagem += (
            f"{numero}. {nome}\n"
            f"   👤 {qualificacao}\n"
        )

        if data_entrada:

            mensagem += (
                f"   📅 Entrada: "
                f"{data_entrada}\n"
            )

        mensagem += "\n"

    keyboard = teclado_qsa(
        pagina,
        total
    )

    await query.message.reply_text(
        mensagem,
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )

    return ESPERANDO_CNPJ


async def qsa_next(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    qsa = context.user_data.get(
        "qsa",
        []
    )

    total_paginas = (
        (
            len(qsa)
            + TAMANHO_PAGINA_QSA
            - 1
        )
        // TAMANHO_PAGINA_QSA
    )

    pagina = context.user_data.get(
        "qsa_pagina",
        0
    )

    if pagina < total_paginas - 1:

        context.user_data[
            "qsa_pagina"
        ] = pagina + 1

    return await mostrar_qsa(
        update,
        context
    )


async def qsa_prev(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    pagina = context.user_data.get(
        "qsa_pagina",
        0
    )

    if pagina > 0:

        context.user_data[
            "qsa_pagina"
        ] = pagina - 1

    return await mostrar_qsa(
        update,
        context
    )


async def qsa_volver(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "🏢 EMPRESA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Usa 🔁 Nueva búsqueda "
        "para consultar otro CNPJ."
    )

    return ESPERANDO_CNPJ


# ============================================================
# RAZÃO SOCIAL
# ============================================================

async def razao_social(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "🏷️ RAZÃO SOCIAL\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce la Razão Social "
        "que quieres investigar.\n\n"
        "Ejemplo:\n"
        "BANCO DO BRASIL SA"
    )

    return ESPERANDO_RAZAO_SOCIAL


async def recibir_razao_social(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    nome = update.message.text.strip()

    resultado = buscar_empresa_por_nome(
        nome,
        "razao_social"
    )

    if resultado is None:

        await update.message.reply_text(
            "❌ Introduce al menos "
            "3 caracteres."
        )

        return ESPERANDO_RAZAO_SOCIAL

    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 Google",
                url=resultado["google"]
            ),
            InlineKeyboardButton(
                "🔢 Buscar CNPJ",
                url=resultado["google_cnpj"]
            ),
        ],
        [
            InlineKeyboardButton(
                "📰 Google News",
                url=resultado["google_news"]
            ),
            InlineKeyboardButton(
                "🔎 Bing",
                url=resultado["bing"]
            ),
        ],
        [
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=resultado["duckduckgo"]
            ),
        ],
        [
            InlineKeyboardButton(
                "🏛️ Buscar en gov.br",
                url=resultado["google_gov"]
            ),
        ],
        [
            InlineKeyboardButton(
                "🗺️ Google Maps",
                url=resultado["google_maps"]
            ),
        ],
    ]

    keyboard.extend(
        teclado_busqueda()
    )

    await update.message.reply_text(
        "🏷️ RAZÃO SOCIAL\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🏢 Empresa:\n"
        f"{resultado['nome']}\n\n"
        "⚠️ Los resultados proceden "
        "de búsquedas públicas.\n"
        "⚠️ Verifica el CNPJ antes de "
        "considerarlo como coincidencia.\n\n"
        "🔎 Búsquedas:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )

    return ESPERANDO_RAZAO_SOCIAL


async def nueva_busqueda_razao_social(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "🔁 RAZÃO SOCIAL\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce la nueva Razão Social:"
    )

    return ESPERANDO_RAZAO_SOCIAL


# ============================================================
# NOME FANTASIA
# ============================================================

async def nome_fantasia(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "🏪 NOME FANTASIA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce el Nome Fantasia "
        "que quieres investigar.\n\n"
        "Ejemplo:\n"
        "DIRECAO GERAL"
    )

    return ESPERANDO_NOME_FANTASIA


async def recibir_nome_fantasia(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    nome = update.message.text.strip()

    resultado = buscar_empresa_por_nome(
        nome,
        "nome_fantasia"
    )

    if resultado is None:

        await update.message.reply_text(
            "❌ Introduce al menos "
            "3 caracteres."
        )

        return ESPERANDO_NOME_FANTASIA

    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 Google",
                url=resultado["google"]
            ),
            InlineKeyboardButton(
                "🔢 Buscar CNPJ",
                url=resultado["google_cnpj"]
            ),
        ],
        [
            InlineKeyboardButton(
                "📰 Google News",
                url=resultado["google_news"]
            ),
            InlineKeyboardButton(
                "🔎 Bing",
                url=resultado["bing"]
            ),
        ],
        [
            InlineKeyboardButton(
                "🦆 DuckDuckGo",
                url=resultado["duckduckgo"]
            ),
        ],
        [
            InlineKeyboardButton(
                "🏛️ Buscar en gov.br",
                url=resultado["google_gov"]
            ),
        ],
        [
            InlineKeyboardButton(
                "🗺️ Google Maps",
                url=resultado["google_maps"]
            ),
        ],
    ]

    keyboard.extend(
        teclado_busqueda()
    )

    await update.message.reply_text(
        "🏪 NOME FANTASIA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🏢 Nombre:\n"
        f"{resultado['nome']}\n\n"
        "⚠️ Los resultados proceden "
        "de búsquedas públicas.\n"
        "⚠️ Verifica el CNPJ antes de "
        "considerarlo como coincidencia.\n\n"
        "🔎 Búsquedas:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )

    return ESPERANDO_NOME_FANTASIA


async def nueva_busqueda_nome_fantasia(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "🔁 NOME FANTASIA\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Introduce el nuevo Nome Fantasia:"
    )

    return ESPERANDO_NOME_FANTASIA


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
        "📱 Introduce el número de teléfono "
        "que quieres investigar:\n\n"
        "Ejemplo:\n"
        "+55 11 99999-9999"
    )

    return ESPERANDO_TELEFONO


async def recibir_telefono(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    telefone_usuario = update.message.text

    resultado = analisar_telefone(
        telefone_usuario
    )

    if resultado is None:

        await update.message.reply_text(
            "❌ El número no tiene un "
            "formato válido."
        )

        return ESPERANDO_TELEFONO

    numero = resultado["numero"]

    numero_internacional = (
        resultado[
            "numero_internacional"
        ]
    )

    busqueda_numero = (
        f'"{numero}"'
    )

    busqueda_internacional = (
        f'"{numero_internacional}"'
    )

    google = (
        "https://www.google.com/search?q="
        + quote_plus(
            busqueda_numero
        )
    )

    google_internacional = (
        "https://www.google.com/search?q="
        + quote_plus(
            busqueda_internacional
        )
    )

    google_news = (
        "https://www.google.com/search?"
        "tbm=nws&q="
        + quote_plus(
            busqueda_numero
        )
    )

    bing = (
        "https://www.bing.com/search?q="
        + quote_plus(
            busqueda_numero
        )
    )

    duckduckgo = (
        "https://duckduckgo.com/?q="
        + quote_plus(
            busqueda_numero
        )
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

    keyboard.extend(
        teclado_busqueda()
    )

    await update.message.reply_text(
        "📱 TELÉFONO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"📞 Número: {numero}\n"
        f"🌎 Internacional: "
        f"+{numero_internacional}\n"
        f"📍 DDD: {resultado['ddd']}\n"
        f"📱 Tipo: {resultado['tipo']}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
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

    resultado = analisar_placa(
        placa_usuario
    )

    if resultado is None:

        await update.message.reply_text(
            "❌ La placa no tiene un formato "
            "brasileño válido."
        )

        return ESPERANDO_PLACA

    placa = resultado["placa"]

    busqueda = (
        f'"{placa}"'
    )

    google = (
        "https://www.google.com/search?q="
        + quote_plus(busqueda)
    )

    google_news = (
        "https://www.google.com/search?"
        "tbm=nws&q="
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

    keyboard.extend(
        teclado_busqueda()
    )

    await update.message.reply_text(
        "🚗 VEHÍCULO\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🔢 Placa: {placa}\n"
        f"📋 Formato: "
        f"{resultado['tipo']}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
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
        "Av. Francisco Matarazzo, "
        "1000, São Paulo - SP\n"
        "05001-100"
    )

    return ESPERANDO_DIRECCION


async def recibir_direccion(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    direccion_usuario = update.message.text

    resultado = analisar_direccion(
        direccion_usuario
    )

    if resultado is None:

        await update.message.reply_text(
            "❌ El dato no parece válido."
        )

        return ESPERANDO_DIRECCION

    direccion_normalizada = (
        resultado["direccion"]
    )

    cep = resultado["cep"]

    datos_cep = resultado["datos_cep"]

    datos_geo = resultado.get(
        "datos_geocodificacion"
    )

    cep_confirmado = resultado.get(
        "cep_confirmado",
        False
    )

    if resultado["es_cep"]:

        if datos_cep is None:

            await update.message.reply_text(
                "❌ No encontramos información "
                "para ese CEP."
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
            f'"{logradouro}" '
            f'"{bairro}" '
            f'"{cidade}" '
            f'"{uf}"'
        )

        google = (
            "https://www.google.com/search?q="
            + quote_plus(consulta)
        )

        google_maps = (
            "https://www.google.com/maps/search/"
            "?api=1&query="
            + quote_plus(
                f"{logradouro}, "
                f"{bairro}, "
                f"{cidade} - {uf}"
            )
        )

        google_news = (
            "https://www.google.com/search?"
            "tbm=nws&q="
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

        keyboard.extend(
            teclado_busqueda()
        )

        await update.message.reply_text(
            "📮 CEP\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"📮 CEP: "
            f"{datos_cep.get('cep', cep)}\n"
            "✅ Confirmado por ViaCEP\n\n"
            f"🏠 Logradouro: "
            f"{logradouro}\n"
            f"🏘️ Bairro: {bairro}\n"
            f"🏙️ Ciudad: {cidade}\n"
            f"🇧🇷 Estado: "
            f"{estado} ({uf})\n"
            f"🌎 Región: {regiao}\n"
            f"📞 DDD: {ddd}\n"
            f"🔢 IBGE: {ibge}\n\n"
            "🔎 Búsquedas públicas:",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            ),
        )

        return ESPERANDO_DIRECCION

    busqueda_direccion = (
        f'"{direccion_normalizada}"'
    )

    google = (
        "https://www.google.com/search?q="
        + quote_plus(
            busqueda_direccion
        )
    )

    google_maps = (
        "https://www.google.com/maps/search/"
        "?api=1&query="
        + quote_plus(
            direccion_normalizada
        )
    )

    google_news = (
        "https://www.google.com/search?"
        "tbm=nws&q="
        + quote_plus(
            busqueda_direccion
        )
    )

    bing = (
        "https://www.bing.com/search?q="
        + quote_plus(
            busqueda_direccion
        )
    )

    duckduckgo = (
        "https://duckduckgo.com/?q="
        + quote_plus(
            busqueda_direccion
        )
    )

    osm_url = (
        "https://www.openstreetmap.org/search?"
        "query="
        + quote_plus(
            direccion_normalizada
        )
    )

    correios = (
        "https://buscacepinter.correios.com.br/"
        "app/localidade_logradouro/index.php"
    )

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
            f"📌 Ubicación: "
            f"{display_name}\n"
            f"🌐 Latitud: "
            f"{latitude}\n"
            f"🌐 Longitud: "
            f"{longitude}\n"
        )

        if geo_logradouro:

            geo_extra += (
                f"🏠 Logradouro: "
                f"{geo_logradouro}\n"
            )

        if geo_numero:

            geo_extra += (
                f"🔢 Número: "
                f"{geo_numero}\n"
            )

        if geo_bairro:

            geo_extra += (
                f"🏘️ Bairro: "
                f"{geo_bairro}\n"
            )

        if geo_cidade:

            geo_extra += (
                f"🏙️ Ciudad: "
                f"{geo_cidade}\n"
            )

        if geo_estado:

            geo_extra += (
                f"🇧🇷 Estado: "
                f"{geo_estado}\n"
            )

        if (
            geo_cep_sugerido
            and not cep_confirmado
        ):

            cep_geo = "".join(
                c
                for c in str(
                    geo_cep_sugerido
                )
                if c.isdigit()
            )

            if len(cep_geo) == 8:

                cep_geo = (
                    f"{cep_geo[:5]}-"
                    f"{cep_geo[5:]}"
                )

            geo_extra += (
                f"📮 CEP sugerido: "
                f"{cep_geo}\n"
                "⚠️ No verificado\n"
            )

    if (
        cep
        and cep_confirmado
        and datos_cep
    ):

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
            f"📮 CEP: "
            f"{datos_cep.get('cep', cep)}\n"
            "✅ Confirmado por ViaCEP\n"
            f"🏠 Logradouro: "
            f"{logradouro}\n"
            f"🏘️ Bairro: {bairro}\n"
            f"🏙️ Ciudad: {cidade}\n"
            f"🇧🇷 Estado: "
            f"{estado} ({uf})\n"
            f"🌎 Región: {regiao}\n"
            f"📞 DDD: {ddd}\n"
            f"🔢 IBGE: {ibge}\n"
        )

    elif cep:

        cep_sugerido = "".join(
            c
            for c in str(cep)
            if c.isdigit()
        )

        if len(cep_sugerido) == 8:

            cep_sugerido = (
                f"{cep_sugerido[:5]}-"
                f"{cep_sugerido[5:]}"
            )

        info_extra = (
            "📮 CEP SUGERIDO\n"
            "━━━━━━━━━━━━━━━━\n"
            f"📮 CEP: "
            f"{cep_sugerido}\n"
            "⚠️ Encontrado por "
            "geocodificación.\n"
            "⚠️ No confirmado por ViaCEP.\n"
        )

    else:

        info_extra = (
            "📮 CEP\n"
            "━━━━━━━━━━━━━━━━\n"
            "📮 CEP: No encontrado "
            "automáticamente\n"
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

    keyboard.extend(
        teclado_busqueda()
    )

    await update.message.reply_text(
        "📍 DIRECCIÓN\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"🏠 Dirección:\n"
        f"{direccion_normalizada}\n\n"
        f"{info_extra}"
        f"{geo_extra}\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
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

    resultado = analisar_dominio(
        dominio_usuario
    )

    if resultado is None:

        await update.message.reply_text(
            "❌ El dominio no tiene "
            "un formato válido."
        )

        return ESPERANDO_DOMINIO

    dominio = resultado["dominio"]

    tld = resultado["tld"]

    subdominio = resultado[
        "subdominio"
    ]

    busqueda = f'"{dominio}"'

    google = (
        "https://www.google.com/search?q="
        + quote_plus(busqueda)
    )

    google_news = (
        "https://www.google.com/search?"
        "tbm=nws&q="
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
        "https://www.google.com/maps/search/"
        "?api=1&query="
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

    keyboard.extend(
        teclado_busqueda()
    )

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
        f"🔗 Subdominio: "
        f"{subdominio_texto}\n\n"
        "🔎 Búsquedas públicas:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
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

        await empresa(
            update,
            context
        )

        return

    await query.answer()

    mensajes = {

        "razao_social":
            "🏷️ Razão Social\n\n"
            "Usa la opción "
            "Razão Social del menú.",

        "nome_fantasia":
            "🏪 Nome Fantasia\n\n"
            "Usa la opción "
            "Nome Fantasia del menú.",
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
            "❌ BOT_TOKEN no está configurado "
            "en el archivo .env"
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

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
                    filters.TEXT
                    & ~filters.COMMAND,
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
                    filters.TEXT
                    & ~filters.COMMAND,
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
            CallbackQueryHandler(
                mostrar_qsa,
                pattern="^qsa_ver$"
            ),
            CallbackQueryHandler(
                qsa_next,
                pattern="^qsa_next$"
            ),
            CallbackQueryHandler(
                qsa_prev,
                pattern="^qsa_prev$"
            ),
            CallbackQueryHandler(
                qsa_volver,
                pattern="^qsa_volver$"
            ),
        ],

        allow_reentry=True,
    )

    # ========================================================
    # RAZÃO SOCIAL
    # ========================================================

    conversacion_razao_social = (
        ConversationHandler(

            entry_points=[
                CallbackQueryHandler(
                    razao_social,
                    pattern="^razao_social$"
                )
            ],

            states={

                ESPERANDO_RAZAO_SOCIAL: [
                    MessageHandler(
                        filters.TEXT
                        & ~filters.COMMAND,
                        recibir_razao_social
                    )
                ]

            },

            fallbacks=[
                CommandHandler(
                    "cancelar",
                    cancelar
                ),
                CallbackQueryHandler(
                    nueva_busqueda_razao_social,
                    pattern="^nueva_busqueda$"
                ),
                CallbackQueryHandler(
                    nueva_busqueda_razao_social,
                    pattern="^nueva_busqueda$"
                ),
                CallbackQueryHandler(
                    menu_principal,
                    pattern="^menu_principal$"
                ),
            ],

            allow_reentry=True,
        )
    )

    # ========================================================
    # NOME FANTASIA
    # ========================================================

    conversacion_nome_fantasia = (
        ConversationHandler(

            entry_points=[
                CallbackQueryHandler(
                    nome_fantasia,
                    pattern="^nome_fantasia$"
                )
            ],

            states={

                ESPERANDO_NOME_FANTASIA: [
                    MessageHandler(
                        filters.TEXT
                        & ~filters.COMMAND,
                        recibir_nome_fantasia
                    )
                ]

            },

            fallbacks=[
                CommandHandler(
                    "cancelar",
                    cancelar
                ),
                CallbackQueryHandler(
                    nueva_busqueda_nome_fantasia,
                    pattern="^nueva_busqueda$"
                ),
                CallbackQueryHandler(
                    menu_principal,
                    pattern="^menu_principal$"
                ),
            ],

            allow_reentry=True,
        )
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
                    filters.TEXT
                    & ~filters.COMMAND,
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
                    filters.TEXT
                    & ~filters.COMMAND,
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
                    filters.TEXT
                    & ~filters.COMMAND,
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
                    filters.TEXT
                    & ~filters.COMMAND,
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
        conversacion_razao_social
    )

    app.add_handler(
        conversacion_nome_fantasia
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

    # ========================================================
    # EJECUCIÓN
    # ========================================================

    print(
        "🤖 Brazil OSINT Bot iniciado..."
    )

    print(
        "Presiona Ctrl+C para detenerlo."
    )

    app.run_polling()


if __name__ == "__main__":

    main()