from urllib.parse import quote_plus


FUENTES_PERSONA = {
    "buscadores": [
        {
            "nombre": "Google",
            "emoji": "🔍",
            "url": "https://www.google.com/search?q={consulta}",
        },
        {
            "nombre": "Google News",
            "emoji": "📰",
            "url": "https://www.google.com/search?tbm=nws&q={consulta}",
        },
        {
            "nombre": "Bing",
            "emoji": "🔎",
            "url": "https://www.bing.com/search?q={consulta}",
        },
        {
            "nombre": "DuckDuckGo",
            "emoji": "🦆",
            "url": "https://duckduckgo.com/?q={consulta}",
        },
    ],

    "redes_sociales": [
        {
            "nombre": "Facebook",
            "emoji": "📘",
            "url": "https://www.google.com/search?q={consulta}+site%3Afacebook.com",
        },
        {
            "nombre": "Instagram",
            "emoji": "📸",
            "url": "https://www.google.com/search?q={consulta}+site%3Ainstagram.com",
        },
        {
            "nombre": "TikTok",
            "emoji": "🎵",
            "url": "https://www.google.com/search?q={consulta}+site%3Atiktok.com",
        },
        {
            "nombre": "X / Twitter",
            "emoji": "🐦",
            "url": "https://www.google.com/search?q={consulta}+site%3Ax.com+OR+site%3Atwitter.com",
        },
    ],

    "profesional": [
        {
            "nombre": "LinkedIn",
            "emoji": "💼",
            "url": "https://www.google.com/search?q={consulta}+site%3Alinkedin.com",
        },
        {
            "nombre": "GitHub",
            "emoji": "🐙",
            "url": "https://www.google.com/search?q={consulta}+site%3Agithub.com",
        },
        {
            "nombre": "YouTube",
            "emoji": "▶️",
            "url": "https://www.google.com/search?q={consulta}+site%3Ayoutube.com",
        },
    ],
}


def buscar_persona(nombre):
    consulta = quote_plus(f'"{nombre}"')

    resultados = {}

    for categoria, fuentes in FUENTES_PERSONA.items():
        resultados[categoria] = []

        for fuente in fuentes:
            resultados[categoria].append(
                {
                    "nombre": fuente["nombre"],
                    "emoji": fuente["emoji"],
                    "url": fuente["url"].format(consulta=consulta),
                }
            )

    return resultados