import re
import requests
from urllib.parse import quote_plus


# ============================================================
# CNPJ
# ============================================================

def limpar_cnpj(cnpj):
    """
    Mantiene solamente letras y números.
    Permite CNPJ numérico y alfanumérico.
    """

    return re.sub(
        r"[^A-Za-z0-9]",
        "",
        cnpj
    ).upper()


def formatar_cnpj(cnpj):
    """
    Formato visual para CNPJ numérico tradicional.
    """

    cnpj = limpar_cnpj(cnpj)

    if len(cnpj) == 14 and cnpj.isdigit():

        return (
            f"{cnpj[:2]}."
            f"{cnpj[2:5]}."
            f"{cnpj[5:8]}/"
            f"{cnpj[8:12]}-"
            f"{cnpj[12:]}"
        )

    return cnpj


def validar_cnpj(cnpj):
    """
    Validación estructural básica.

    Acepta:
    - CNPJ numérico de 14 posiciones
    - CNPJ alfanumérico de 14 posiciones
    """

    cnpj = limpar_cnpj(cnpj)

    if len(cnpj) != 14:
        return False

    return True


# ============================================================
# CONSULTA POR CNPJ
# ============================================================

def consultar_cnpj(cnpj):
    """
    Consulta datos públicos mediante MUAC.
    """

    cnpj = limpar_cnpj(cnpj)

    if not validar_cnpj(cnpj):
        return None

    try:

        url = (
            f"https://api.muac.com.br/cnpj/"
            f"{cnpj}"
        )

        resposta = requests.get(
            url,
            timeout=15
        )

        if resposta.status_code == 404:
            return None

        if resposta.status_code != 200:
            return None

        dados = resposta.json()

        if not dados:
            return None

        return dados

    except (
        requests.RequestException,
        ValueError
    ):

        return None


def buscar_empresa_por_cnpj(cnpj):
    """
    Consulta una empresa por CNPJ.
    """

    cnpj_limpo = limpar_cnpj(cnpj)

    if not validar_cnpj(cnpj_limpo):
        return None

    dados = consultar_cnpj(
        cnpj_limpo
    )

    if dados is None:
        return None

    return {
        "cnpj": cnpj_limpo,
        "cnpj_formatado": formatar_cnpj(
            cnpj_limpo
        ),
        "dados": dados,
    }


# ============================================================
# BÚSQUEDA POR RAZÃO SOCIAL / NOME FANTASIA
# ============================================================

def limpar_nome_empresa(nome):
    """
    Limpieza básica del nombre de empresa.
    """

    nome = nome.strip()

    nome = re.sub(
        r"\s+",
        " ",
        nome
    )

    return nome


def buscar_empresa_por_nome(
    nome,
    tipo="razao_social"
):
    """
    Genera búsquedas públicas especializadas.

    No afirma que los resultados encontrados por buscadores
    sean registros oficiales. Sirve como etapa OSINT para
    descubrir posibles CNPJs y fuentes públicas.
    """

    nome = limpar_nome_empresa(
        nome
    )

    if len(nome) < 3:
        return None

    termo = quote_plus(
        f'"{nome}"'
    )

    if tipo == "nome_fantasia":

        titulo = (
            "Nome Fantasia"
        )

        consulta_base = (
            f'"{nome}" '
            f'empresa CNPJ'
        )

    else:

        titulo = (
            "Razão Social"
        )

        consulta_base = (
            f'"{nome}" '
            f'CNPJ'
        )

    consulta = quote_plus(
        consulta_base
    )

    consulta_cnpj = quote_plus(
        f'"{nome}" "CNPJ"'
    )

    consulta_gov = quote_plus(
        f'"{nome}"'
    )

    consulta_maps = quote_plus(
        nome
    )

    return {
        "nome": nome,
        "tipo": tipo,
        "titulo": titulo,

        "google": (
            "https://www.google.com/search?q="
            + consulta
        ),

        "google_cnpj": (
            "https://www.google.com/search?q="
            + consulta_cnpj
        ),

        "google_news": (
            "https://www.google.com/search?"
            "tbm=nws&q="
            + termo
        ),

        "bing": (
            "https://www.bing.com/search?q="
            + consulta
        ),

        "duckduckgo": (
            "https://duckduckgo.com/?q="
            + consulta
        ),

        "google_gov": (
            "https://www.google.com/search?q="
            + quote_plus(
                consulta_base
                + " site:gov.br"
            )
        ),

        "google_maps": (
            "https://www.google.com/maps/search/"
            "?api=1&query="
            + consulta_maps
        ),
    }