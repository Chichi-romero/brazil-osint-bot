import re


def limpiar_telefone(telefone):
    """Elimina espacios, paréntesis, guiones y otros caracteres."""

    return re.sub(r"\D", "", telefone)


def analisar_telefone(telefone):
    """Analiza un número telefónico brasileño."""

    numero = limpiar_telefone(telefone)

    # Elimina el código de país 55 si fue incluido
    if numero.startswith("55") and len(numero) in (12, 13):
        numero = numero[2:]

    # Un teléfono brasileño debe tener 10 u 11 dígitos:
    # 10 = fijo: DDD + 8 dígitos
    # 11 = celular: DDD + 9 dígitos
    if len(numero) not in (10, 11):
        return None

    ddd = numero[:2]
    telefone_local = numero[2:]

    tipo = "Celular" if len(numero) == 11 else "Fixo"

    return {
        "numero": numero,
        "ddd": ddd,
        "telefone_local": telefone_local,
        "tipo": tipo,
        "numero_internacional": f"55{numero}",
    }