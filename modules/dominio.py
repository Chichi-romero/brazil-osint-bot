import re


def limpiar_dominio(dominio):
    """Normaliza un dominio eliminando protocolo y rutas."""

    dominio = dominio.strip().lower()

    dominio = re.sub(r"^https?://", "", dominio)
    dominio = re.sub(r"^www\.", "", dominio)
    dominio = dominio.split("/")[0]

    return dominio


def analisar_dominio(dominio):
    """Valida y analiza un dominio de forma básica."""

    dominio = limpiar_dominio(dominio)

    patron = r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"

    if not re.match(patron, dominio):
        return None

    partes = dominio.split(".")

    return {
        "dominio": dominio,
        "tld": partes[-1],
        "subdominio": ".".join(partes[:-2]) if len(partes) > 2 else None,
    }