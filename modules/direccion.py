import re
import requests


def limpiar_texto(texto):
    texto = texto.strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def limpar_cep(cep):
    return re.sub(r"\D", "", cep)


def formatar_cep(cep):
    cep = limpar_cep(cep)

    if len(cep) == 8:
        return f"{cep[:5]}-{cep[5:]}"

    return cep


def detectar_cep(texto):
    match = re.search(r"\b\d{5}-?\d{3}\b", texto)

    if not match:
        return None

    return limpar_cep(match.group(0))


def normalizar_logradouro(texto):
    if not texto:
        return ""

    texto = texto.lower().strip()

    abreviacoes = {
        "av.": "avenida",
        "av": "avenida",
        "r.": "rua",
        "r": "rua",
        "rod.": "rodovia",
        "rod": "rodovia",
        "al.": "alameda",
        "al": "alameda",
        "trav.": "travessa",
        "trav": "travessa",
    }

    palavras = texto.split()

    resultado = []

    for palavra in palavras:
        resultado.append(
            abreviacoes.get(palavra, palavra)
        )

    texto = " ".join(resultado)

    texto = re.sub(r"[^a-z0-9áéíóúãõâêôç\s]", "", texto)

    return texto


def comparar_logradouros(logradouro1, logradouro2):
    a = normalizar_logradouro(logradouro1)
    b = normalizar_logradouro(logradouro2)

    if not a or not b:
        return False

    return a == b or a in b or b in a


def consultar_cep(cep):
    cep = limpar_cep(cep)

    if len(cep) != 8:
        return None

    try:
        url = f"https://viacep.com.br/ws/{cep}/json/"

        resposta = requests.get(
            url,
            timeout=10
        )

        if resposta.status_code != 200:
            return None

        dados = resposta.json()

        if dados.get("erro"):
            return None

        return {
            "cep": dados.get("cep"),
            "logradouro": dados.get("logradouro"),
            "complemento": dados.get("complemento"),
            "bairro": dados.get("bairro"),
            "cidade": dados.get("localidade"),
            "uf": dados.get("uf"),
            "estado": dados.get("estado"),
            "regiao": dados.get("regiao"),
            "ibge": dados.get("ibge"),
            "ddd": dados.get("ddd"),
        }

    except requests.RequestException:
        return None


def validar_cep_sugerido(
    cep,
    dados_geocodificacao
):
    if not cep or not dados_geocodificacao:
        return None

    dados_cep = consultar_cep(cep)

    if not dados_cep:
        return None

    logradouro_geo = (
        dados_geocodificacao.get("logradouro")
    )

    cidade_geo = (
        dados_geocodificacao.get("cidade")
    )

    estado_geo = (
        dados_geocodificacao.get("estado")
    )

    cidade_cep = dados_cep.get("cidade")
    estado_cep = dados_cep.get("estado")
    logradouro_cep = dados_cep.get("logradouro")

    logradouro_ok = comparar_logradouros(
        logradouro_geo,
        logradouro_cep
    )

    cidade_ok = (
        bool(cidade_geo)
        and bool(cidade_cep)
        and cidade_geo.lower() == cidade_cep.lower()
    )

    estado_ok = (
        bool(estado_geo)
        and bool(estado_cep)
        and estado_geo.lower() == estado_cep.lower()
    )

    confirmado = (
        logradouro_ok
        and cidade_ok
        and estado_ok
    )

    return {
        "confirmado": confirmado,
        "cep": formatar_cep(cep),
        "dados_cep": dados_cep,
        "logradouro_ok": logradouro_ok,
        "cidade_ok": cidade_ok,
        "estado_ok": estado_ok,
    }


def consultar_endereco_nominatim(endereco):
    """
    Usa Nominatim únicamente para geocodificación.

    El CEP devuelto por Nominatim se considera solamente
    un candidato hasta ser validado por ViaCEP.
    """

    try:
        url = "https://nominatim.openstreetmap.org/search"

        parametros = {
            "q": f"{endereco}, Brasil",
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": 1,
        }

        headers = {
            "User-Agent": "BrazilOSINT/1.0"
        }

        resposta = requests.get(
            url,
            params=parametros,
            headers=headers,
            timeout=10
        )

        if resposta.status_code != 200:
            return None

        resultados = resposta.json()

        if not resultados:
            return None

        resultado = resultados[0]
        endereco_detalhado = resultado.get("address", {})

        return {
            "display_name": resultado.get("display_name"),
            "latitude": resultado.get("lat"),
            "longitude": resultado.get("lon"),
            "cep_sugerido": endereco_detalhado.get("postcode"),
            "logradouro": (
                endereco_detalhado.get("road")
                or endereco_detalhado.get("pedestrian")
            ),
            "numero": endereco_detalhado.get("house_number"),
            "bairro": (
                endereco_detalhado.get("suburb")
                or endereco_detalhado.get("neighbourhood")
            ),
            "cidade": (
                endereco_detalhado.get("city")
                or endereco_detalhado.get("town")
                or endereco_detalhado.get("municipality")
            ),
            "estado": endereco_detalhado.get("state"),
            "uf": endereco_detalhado.get("ISO3166-2-lvl4"),
        }

    except requests.RequestException:
        return None


def analisar_direccion(direccion):

    direccion = limpiar_texto(direccion)

    if len(direccion) < 5:
        return None

    cep = detectar_cep(direccion)

    es_cep = bool(
        re.fullmatch(
            r"\d{5}-?\d{3}",
            direccion
        )
    )

    resultado = {
        "direccion": direccion,
        "cep": cep,
        "es_cep": es_cep,
        "datos_cep": None,
        "datos_geocodificacion": None,
        "validacion_cep": None,
        "cep_confirmado": False,
    }

    # ========================================================
    # CASO 1: EL USUARIO INTRODUJO DIRECTAMENTE UN CEP
    # ========================================================

    if cep:

        datos_cep = consultar_cep(cep)

        if datos_cep:
            resultado["datos_cep"] = datos_cep
            resultado["cep"] = limpar_cep(
                datos_cep["cep"]
            )
            resultado["cep_confirmado"] = True

        return resultado

    # ========================================================
    # CASO 2: EL USUARIO INTRODUJO UNA DIRECCIÓN
    # ========================================================

    datos_geo = consultar_endereco_nominatim(direccion)

    if not datos_geo:
        return resultado

    resultado["datos_geocodificacion"] = datos_geo

    cep_sugerido = datos_geo.get("cep_sugerido")

    if not cep_sugerido:
        return resultado

    cep_sugerido = limpar_cep(cep_sugerido)

    resultado["cep"] = cep_sugerido

    validacion = validar_cep_sugerido(
        cep_sugerido,
        datos_geo
    )

    resultado["validacion_cep"] = validacion

    if validacion:

        resultado["datos_cep"] = validacion["dados_cep"]

        if validacion["confirmado"]:
            resultado["cep_confirmado"] = True

    return resultado