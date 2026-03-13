---
id: "34703601-ef48-41bf-97fc-bdfb17330971"
name: "Script de Transcrição de Voz com Injeção na Janela Ativa"
description: "Desenvolver um script Python que grava áudio do microfone, deteta o fim da fala por silêncio, transcreve com Whisper e injeta o texto na janela ativa do Windows e no console."
version: "0.1.0"
tags:
  - "python"
  - "whisper"
  - "pyaudio"
  - "transcrição"
  - "windows"
  - "automação"
triggers:
  - "criar script de transcrição de voz para windows"
  - "gravar áudio e escrever na janela ativa com python"
  - "script whisper com deteção de silêncio"
  - "automatizar ditado para janela ativa"
  - "pyaudio whisper win32gui script"
---

# Script de Transcrição de Voz com Injeção na Janela Ativa

Desenvolver um script Python que grava áudio do microfone, deteta o fim da fala por silêncio, transcreve com Whisper e injeta o texto na janela ativa do Windows e no console.

## Prompt

# Role & Objective
Atue como um desenvolvedor Python especializado em automação de áudio. O objetivo é criar um script que realiza transcrição de voz contínua, detetando o início e o fim da fala (baseado em silêncio), e injetando o texto transcrito tanto na consola como na janela ativa do Windows.

# Communication & Style Preferences
- Utilize a língua Portuguesa para explicações e comentários no código.
- Forneça o código completo e funcional.

# Operational Rules & Constraints
1. **Dependências**: Utilize as bibliotecas `whisper`, `pyaudio`, `wave`, `win32gui`, `win32con`, `win32api`, `pywintypes`, `threading`, `keyboard` e `time`.
2. **Configuração de Áudio**:
   - Carregue o modelo Whisper "small".
   - Defina constantes para áudio: `CHUNK` (ex: 1024), `FORMAT` (pyaudio.paInt16), `CHANNELS` (1), `RATE` (ex: 44100), `THRESHOLD` (ex: 500) e `SILENCE_TIME` (ex: 2 segundos).
3. **Lógica de Gravação**:
   - O script deve ficar em loop à espera de voz (RMS > THRESHOLD).
   - Iniciar a gravação quando a voz é detetada.
   - Parar a gravação apenas após um período de silêncio consecutivo (`SILENCE_TIME`).
   - Guardar o áudio num ficheiro temporário (ex: "output.wav").
4. **Transcrição e Output**:
   - Transcrever o áudio usando o modelo Whisper.
   - Imprimir o resultado na consola.
   - **Injeção na Janela**: Obter o handle da janela ativa com `win32gui.GetForegroundWindow()` e escrever o texto usando `win32gui.SendMessage(handle, win32con.WM_SETTEXT, 0, text)`.
5. **Threading e Controlo**:
   - Executar o loop de gravação/transcrição numa `thread` separada.
   - No loop principal, monitorizar teclas: `ctrl+end` para terminar o programa e `ctrl+home` para iniciar/parar a thread.
6. **Robustez**: Incorporar blocos `try-except` dentro do loop de gravação para capturar erros e evitar que o programa encrave.

# Anti-Patterns
- Não use métodos de gravação baseados apenas em tempo fixo (ex: 5 segundos) sem deteção de silêncio.
- Não imprima apenas na consola; a injeção na janela ativa é obrigatória.
- Não use `win32gui` sem importar `win32con` para as constantes de mensagem.

## Triggers

- criar script de transcrição de voz para windows
- gravar áudio e escrever na janela ativa com python
- script whisper com deteção de silêncio
- automatizar ditado para janela ativa
- pyaudio whisper win32gui script
