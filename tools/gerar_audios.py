"""Gera os áudios (voz neural) das frases prontas e do vocabulário.

Uso:  pip install edge-tts
      python tools/gerar_audios.py

Cria audio/<voz>/<hash>.mp3 e audio/vozes.json:
  {"vozes": {"antonio": "Antonio (masculina)", ...}, "teste": "...",
   "frases": {"texto": "hash"},                    # frases prontas (gravação inteira)
   "palavras": {"palavra": "hash"},                # botões de "Montar frase" (baixadas p/ uso offline)
   "extras": {"palavra": "hash"}}                  # vocabulário grande (baixado quando usado)
O áudio fica em audio/<voz>/<hash>.mp3.
Rode de novo sempre que mudar frases/palavras no index.html ou nas listas de tools/.
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
PARALELO = 6

# Palavras curtas que, sozinhas, a voz leria "tônicas" ou como letra ("o" → "ó").
# Aqui vai como devem SOAR dentro de uma frase.
PRONUNCIA = {"e": "i", "o": "u", "os": "us", "de": "di", "do": "du", "dos": "dus",
             "no": "nu", "nos": "nus", "se": "si", "te": "tchi", "me": "mi", "lhe": "lhi", "que": "qui"}

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "audio"
TOOLS = ROOT / "tools"
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


def lista_arquivo(nome):
    linhas = (TOOLS / nome).read_text(encoding="utf-8").splitlines()
    return [l.strip().lower() for l in linhas if l.strip() and not l.startswith("#")]


def extras(ja):
    """Vocabulário grande para o texto digitado: saúde + mais frequentes + números."""
    lista = lista_arquivo("vocabulario_saude.txt") + lista_arquivo("frequentes.txt")
    lista += [str(n) for n in range(0, 101)]
    return [p for p in dict.fromkeys(lista) if p not in ja]


def chave(texto):
    return hashlib.md5(texto.encode("utf-8")).hexdigest()[:10]


async def main():
    fr = {t: chave(t) for t in frases()}
    pa = {p: chave(PRONUNCIA.get(p, p) + "|palavra") for p in palavras()}
    ex = {p: chave(PRONUNCIA.get(p, p) + "|palavra") for p in extras(set(pa))}

    # hash → texto a falar
    falar = {h: t for t, h in fr.items()}
    falar.update({h: PRONUNCIA.get(p, p) for p, h in list(pa.items()) + list(ex.items())})

    sem = asyncio.Semaphore(PARALELO)
    feitos = 0

    async def gerar(pasta, voz, h, texto):
        nonlocal feitos
        destino = OUT / pasta / (h + ".mp3")
        if destino.exists():
            return
        async with sem:
            for tentativa in range(4):
                try:
                    await edge_tts.Communicate(texto, voz, rate=RATE, volume=VOLUME).save(str(destino))
                    break
                except Exception as e:
                    destino.unlink(missing_ok=True)
                    if tentativa == 3:
                        print("FALHOU:", pasta, texto, e)
                    await asyncio.sleep(2 * (tentativa + 1))
        feitos += 1
        if feitos % 200 == 0:
            print(feitos, "gerados...", flush=True)

    for pasta, (_, voz) in VOZES.items():
        (OUT / pasta).mkdir(parents=True, exist_ok=True)
        await asyncio.gather(*(gerar(pasta, voz, h, t) for h, t in falar.items()))

    # remove áudios que não são mais usados (e arquivos antigos)
    for f in OUT.rglob("*.mp3"):
        if f.parent.name not in VOZES or f.stem not in falar:
            f.unlink()
    for antigo in ("frases.json", "palavras.json"):
        (OUT / antigo).unlink(missing_ok=True)

    indice = {"vozes": {k: v[0] for k, v in VOZES.items()}, "teste": TESTE,
              "frases": fr, "palavras": pa, "extras": ex}
    (OUT / "vozes.json").write_text(json.dumps(indice, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(fr), "frases,", len(pa), "palavras dos botões,", len(ex), "palavras extras")


asyncio.run(main())
