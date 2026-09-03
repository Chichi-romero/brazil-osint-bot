import re


def limpiar_texto(texto):
    """Normaliza espacios y caracteres básicos."""

    texto = texto.strip()
    texto = re.sub(r"\s+", " ", texto)

    return texto


def analisar_direccion(direccion):
    """Analiza una dirección brasileña de forma básica."""

    direccion = limpiar_texto(direccion)

    if len(direccion) < 5:
        return None

    cep_match = re.search(
        r"\b\d{5}-?\d{3}\b",
        direccion
    )

    cep = cep_match.group(0) if cep_match else None

    if cep:
        cep = cep.replace("-", "")

    return {
        "direccion": direccion,
        "cep": cep,
    }