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

Duas vozes gravadas (neural, iguais em qualquer celular): **Antonio** e **Francisca**. A escolha fica no fim da página.

- Frases prontas usam a gravação inteira.
- Frases montadas ou digitadas juntam as gravações de cada palavra. O vocabulário tem os botões, cerca de 3.500 palavras mais usadas do português (`tools/frequentes.txt`), termos de saúde e hospital (`tools/vocabulario_saude.txt`) e números de 0 a 100.
- Só se faltar alguma palavra é usada a voz do próprio celular (apenas vozes do Brasil). O app mostra quais palavras faltaram.

Para acrescentar palavras, coloque-as em `tools/vocabulario_saude.txt` e gere os áudios de novo:

```
pip install edge-tts
python tools/gerar_audios.py
```
