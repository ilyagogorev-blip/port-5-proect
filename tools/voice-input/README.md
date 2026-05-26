# Voice Input — голосовой ввод через Groq Whisper

Скрипт записывает голос по нажатию Mouse5 и вставляет транскрибированный текст прямо в активное поле ввода.

## Как работает

1. **Mouse5 (первый раз)** → начинает запись микрофона
2. **Mouse5 (второй раз)** → останавливает запись, отправляет в Groq Whisper
3. Текст автоматически печатается в то поле, где стоит курсор

## Стек

- **Groq Whisper** (`whisper-large-v3-turbo`) — транскрибация
- **sounddevice** — запись с микрофона
- **pynput** — отслеживание Mouse5 + симуляция ввода

## Установка

```
pip install groq sounddevice numpy pynput
```

## Запуск

```
python "C:\Users\SHINU TSUMORI\OneDrive\Документы\projects-ai\.claude\1-proect-vs\tools\voice-input\voice.py"
```

## Автозапуск с Windows

Создать `.vbs` файл в папке автозагрузки (`shell:startup`):

```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python ""C:\Users\SHINU TSUMORI\OneDrive\Документы\projects-ai\.claude\1-proect-vs\tools\voice-input\voice.py""", 0, False
```

## Настройки

- `GROQ_API_KEY` — ключ в строке 12 файла `voice.py`
- `language="ru"` — язык транскрибации (строка 48)
- `SAMPLE_RATE = 16000` — частота записи (менять не нужно)
