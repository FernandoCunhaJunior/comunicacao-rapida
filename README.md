# Comunicação Rápida

Página simples para quem está sem conseguir falar (ex.: após cirurgia) se comunicar pelo celular:

- **Frases rápidas** com 1 toque (dor, água, banheiro, chamar equipe…)
- **Montar frase** tocando palavras em sequência (ex.: *Está doendo* → *na garganta*)
- **Nível de dor** de 0 a 10
- **Falar** (voz do celular em português) e **Grande** (texto em tela cheia para mostrar)
- Botões fixos **SIM / NÃO / AJUDA** sempre visíveis
- Funciona **sem internet** depois de aberto uma vez

## Instalar no celular

Abra o link do GitHub Pages no celular e:

- **iPhone (Safari):** Compartilhar → *Adicionar à Tela de Início*
- **Android (Chrome):** menu ⋮ → *Adicionar à tela inicial* / *Instalar app*

## Voz

As frases prontas usam áudios gravados com voz neural (`audio/`). Depois de mudar ou acrescentar frases no `index.html`, gere os áudios de novo:

```
pip install edge-tts
python tools/gerar_audios.py
```

Frases montadas palavra por palavra ou digitadas usam a voz do próprio celular (dá para escolher a voz no fim da página).
