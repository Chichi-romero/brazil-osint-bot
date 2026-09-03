import re


def limpiar_placa(placa):
    """Elimina espacios, guiones y caracteres especiales."""

    return re.sub(r"[^A-Za-z0-9]", "", placa).upper()


def analisar_placa(placa):
    """Analiza una placa brasileña."""

    placa = limpiar_placa(placa)

    # Formato antiguo: ABC1234
    formato_antiguo = r"^[A-Z]{3}[0-9]{4}$"

    # Formato Mercosur: ABC1D23
    formato_mercosur = r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$"

    if re.match(formato_antiguo, placa):
        tipo = "Formato antiguo"

    elif re.match(formato_mercosur, placa):
        tipo = "Mercosur"

    else:
        return None

    return {
        "placa": placa,
        "tipo": tipo,
    }