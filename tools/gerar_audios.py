"""Gera os áudios (voz neural) das frases prontas e das palavras do index.html.

Uso:  pip install edge-tts
      python tools/gerar_audios.py

Cria audio/<voz>/<hash>.mp3 e audio/vozes.json:
  {"antonio": {"nome": ..., "frases": {"texto": "audio/antonio/x.mp3"}, "palavras": {...}}, ...}
Rode de novo sempre que mudar/acrescentar frases ou palavras no index.html.
"""
import asyncio, hashlib, json, pathlib, re

import edge_tts

VOZES = {
    "antonio": ("Antonio (masculina)", "pt-BR-AntonioNeural"),
    "francisca": ("Francisca (feminina)", "pt-BR-FranciscaNeural"),
}
RATE = "-8%"                   # um pouco mais devagar, mais claro
VOLUME = "+30%"
TESTE = "Olá, esta é a minha voz."

# Palavras muito curtas que, sozinhas, a voz leria como letra ("o" → "ó").
# Aqui vai como deve SOAR.
PRONUNCIA = {"e": "i", "o": "u", "de": "di"}

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "audio"
html = (ROOT / "index.html").read_text(encoding="utf-8")


def frases():
    textos = [TESTE]
    # Frases rápidas: ["rótulo","Texto falado","classe"(,"Aba")]
    quick = re.search(r"var quick = \[(.*?)\n  \];", html, re.S).group(1)
    for m in re.finditer(r'\["[^"]*","([^"]*)"', quick):
        textos.append(m.group(1))
    # Botões fixos SIM / NÃO / AJUDA
    textos += re.findall(r'data-fixed="([^"]*)"', html)
    # "Está doendo" + parte do corpo (frase montada mais comum)
    corpo = re.search(r'"Corpo":\[(.*?)\]', html).group(1)
    for parte in re.findall(r'"([^"]*)"', corpo):
        textos.append(f"Está doendo {parte}.")
    # Escala de dor
    textos.append("Estou sem dor (0 de 10).")
    textos += [f"Minha dor está em {n} de 10." for n in range(1, 11)]
    # só frases completas (a "Está doendo" sozinha não é falada)
    return list(dict.fromkeys(t for t in textos if re.search(r"[.!?]$", t)))


def palavras():
    """Cada botão de "Montar frase" vira um áudio; o app junta na ordem tocada."""
    bloco = re.search(r"var categories = \{(.*?)\n  \};", html, re.S).group(1)
    lista = ["Está doendo"]  # início usado pelo botão "Onde dói…"
    for linha in re.findall(r"\[(.*?)\]", bloco):
        lista += re.findall(r'"([^"]*)"', linha)
    return list(dict.fromkeys(p.lower() for p in lista))


async def gerar(pasta, voz, texto, sufixo=""):
    nome = hashlib.md5((texto + sufixo).encode("utf-8")).hexdigest()[:10] + ".mp3"
    destino = OUT / pasta / nome
    if not destino.exists():
        await edge_tts.Communicate(texto, voz, rate=RATE, volume=VOLUME).save(str(destino))
        print(pasta, "gerado:", texto)
    return f"audio/{pasta}/{nome}"


async def main():
    indice = {}
    usados = set()
    for pasta, (nome, voz) in VOZES.items():
        (OUT / pasta).mkdir(parents=True, exist_ok=True)
        fr = {t: await gerar(pasta, voz, t) for t in frases()}
        pa = {p: await gerar(pasta, voz, PRONUNCIA.get(p, p), "|palavra") for p in palavras()}
        indice[pasta] = {"nome": nome, "teste": TESTE, "frases": fr, "palavras": pa}
        usados |= {str(ROOT / u) for u in list(fr.values()) + list(pa.values())}
    # remove áudios que não são mais usados (inclui versões antigas soltas em audio/)
    for f in OUT.rglob("*.mp3"):
        if str(f) not in {str(pathlib.Path(u)) for u in usados}:
            f.unlink()
    for antigo in ("frases.json", "palavras.json"):
        (OUT / antigo).unlink(missing_ok=True)
    (OUT / "vozes.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: (len(v["frases"]), len(v["palavras"])) for k, v in indice.items()})


asyncio.run(main())
