import re
from urllib.parse import quote_plus


def limpiar_cnpj(cnpj):
    """Elimina puntos, barras y guiones del CNPJ."""
    return re.sub(r"\D", "", cnpj)


def validar_cnpj(cnpj):
    """Valida el formato básico de un CNPJ."""
    cnpj = limpiar_cnpj(cnpj)

    if len(cnpj) != 14:
        return False

    if len(set(cnpj)) == 1:
        return False

    return True


def buscar_empresa_por_cnpj(cnpj):
    """Genera búsquedas públicas utilizando un CNPJ válido."""

    cnpj_limpio = limpiar_cnpj(cnpj)

    if not validar_cnpj(cnpj_limpio):
        return None

    consulta = quote_plus(f'"{cnpj_limpio}"')

    return {
        "cnpj": cnpj_limpio,
        "google": f"https://www.google.com/search?q={consulta}",
        "google_news": f"https://www.google.com/search?tbm=nws&q={consulta}",
        "bing": f"https://www.bing.com/search?q={consulta}",
        "duckduckgo": f"https://duckduckgo.com/?q={consulta}",
    }