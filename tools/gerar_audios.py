"""Gera os áudios (voz neural) das frases prontas do index.html.

Uso:  pip install edge-tts
      python tools/gerar_audios.py

Cria audio/<hash>.mp3 e audio/frases.json ({"texto": "audio/arquivo.mp3"}).
Rode de novo sempre que mudar/acrescentar frases no index.html.
"""
import asyncio, hashlib, json, pathlib, re

import edge_tts

VOICE = "pt-BR-AntonioNeural"   # masculina; alternativa: pt-BR-FranciscaNeural
RATE = "-8%"                   # um pouco mais devagar, mais claro
VOLUME = "+30%"

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "audio"
html = (ROOT / "index.html").read_text(encoding="utf-8")


def frases():
    textos = []
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


async def main():
    OUT.mkdir(exist_ok=True)
    mapa = {}
    for texto in frases():
        nome = hashlib.md5(texto.encode("utf-8")).hexdigest()[:10] + ".mp3"
        destino = OUT / nome
        if not destino.exists():
            await edge_tts.Communicate(texto, VOICE, rate=RATE, volume=VOLUME).save(str(destino))
            print("gerado:", texto)
        mapa[texto] = "audio/" + nome
    # remove áudios que não são mais usados
    usados = {pathlib.Path(p).name for p in mapa.values()}
    for f in OUT.glob("*.mp3"):
        if f.name not in usados:
            f.unlink()
    (OUT / "frases.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(mapa), "frases")


asyncio.run(main())
