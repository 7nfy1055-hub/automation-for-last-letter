# automation-for-last-letter
it an automation for the roblox game last letter

# Last Letter Automation

A simple desktop tool for the Roblox game **Last Letter** that quickly finds a matching word and types it for you.

Just enter the starting letters, press **Play**, and the app will automatically type the completed word in Roblox.

---

## Features

*  Finds valid word completions
*  Choose how words are selected:

  * Random
  * Shortest
  * Longest
* Adjustable typing speed
*  Keeps a history of used words to avoid repeats
* Detects whether Roblox is running
* Keyboard shortcut (**Ctrl + Enter**) to play

---

## How to Use

1. Open **Roblox** and join a game of **Last Letter**.
2. Launch **Last Letter Automation**.
3. Enter the starting letters shown in the game.
4. Press **Enter**, **Ctrl + Enter**, or click **Play**.
5. The app will focus Roblox and automatically type the completed word.

---

## Requirements

* Windows 10 or Windows 11
* Roblox installed
* Last Letter game running

If running from source:

* Python 3.8+
* Required packages from `requirements.txt`

---

## Installation

### Run from Source

```bash
git clone <repository-url>
cd <repository-folder>
pip install -r requirements.txt
python last_letter_automation.py
```

### Executable

Download the latest release from the **Releases** page and run the executable. No installation is required.

---

## Dependencies

* keyboard
* tkinter
* packaging
* requests
* english-words

Optional:

* pyinstaller (for building an executable)

---

## Build

Create a standalone executable with:

```bash
pyinstaller --onefile --windowed --icon=LastLetter.ico last_letter_automation.py
```

---


---

## Credits

Created by **lopo**.

The included word list is provided by the **english-words** package, with additional fallback words for offline use.
