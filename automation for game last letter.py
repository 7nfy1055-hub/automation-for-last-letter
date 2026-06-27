"""

"""

import threading
import time
import random
import subprocess
import ctypes
import sys
import os
import json
import urllib.request
from typing import Optional, List, Set

try:
    import keyboard
except ImportError:
    print("Please install keyboard: pip install keyboard")
    sys.exit(1)

try:
    import tkinter as tk
    from tkinter import messagebox
    import tkinter.ttk as ttk
except ImportError:
    print("tkinter is required but not available")
    sys.exit(1)

CURRENT_VERSION = "1.0.0"

class LastLetterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Last Letter Automation")
        self.root.geometry("500x420")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)

        self.bg_color = "#0a0a12"
        self.card_color = "#111122"
        self.accent_color = "#00ffcc"
        self.accent_dim = "#00ccaa"
        self.text_color = "#e0e0ff"
        self.sub_text = "#8888bb"
        self.input_bg = "#1a1a2e"
        self.border_color = "#00ffcc66"
        self.success_color = "#00ff88"
        self.error_color = "#ff4466"

        self.root.configure(bg=self.bg_color)

        self.wordlist: List[str] = []
        self.wordlist_loaded = False
        self.wordlist_error: Optional[Exception] = None
        self.used_words: Set[str] = set()

        self.prefix_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="Short")

        self._build_ui()

        threading.Thread(target=self.load_wordlist, daemon=True).start()
        self.refresh_roblox_status()
        self.root.bind("<FocusIn>", lambda event: self.entry.focus_set())

    def _build_ui(self) -> None:
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=25, pady=20)
        main_frame.pack(fill="both", expand=True)

        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 15))

        title_label = tk.Label(
            header_frame,
            text="⚡ LAST LETTER AUTOMATION",
            font=("Segoe UI", 16, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(side="left")

        status_frame = tk.Frame(header_frame, bg=self.bg_color)
        status_frame.pack(side="right")

        self.status_dot = tk.Label(
            status_frame,
            text="⬤",
            font=("Segoe UI", 12),
            fg=self.error_color,
            bg=self.bg_color
        )
        self.status_dot.pack(side="left", padx=(0, 5))

        self.roblox_status_var = tk.StringVar(value="OFFLINE")
        roblox_status = tk.Label(
            status_frame,
            textvariable=self.roblox_status_var,
            font=("Segoe UI", 9, "bold"),
            fg=self.sub_text,
            bg=self.bg_color
        )
        roblox_status.pack(side="left")

        input_card = tk.Frame(
            main_frame,
            bg=self.card_color,
            padx=15,
            pady=15,
            highlightbackground=self.accent_color,
            highlightthickness=2
        )
        input_card.pack(fill="x", pady=(0, 12))

        label = tk.Label(
            input_card,
            text="» STARTING LETTERS «",
            font=("Segoe UI", 10, "bold"),
            fg=self.accent_color,
            bg=self.card_color
        )
        label.pack(anchor="w", pady=(0, 6))

        entry_frame = tk.Frame(input_card, bg=self.card_color)
        entry_frame.pack(fill="x", pady=(0, 8))

        self.entry = tk.Entry(
            entry_frame,
            textvariable=self.prefix_var,
            font=("Segoe UI", 14),
            bg=self.input_bg,
            fg=self.text_color,
            insertbackground=self.accent_color,
            relief="solid",
            bd=2,
            highlightthickness=2,
            highlightcolor=self.accent_color,
            highlightbackground=self.accent_color
        )
        self.entry.pack(fill="x", ipady=4)
        self.entry.focus_set()
        self.entry.bind("<Control-Return>", self.on_ctrl_enter)
        self.entry.bind("<Return>", self.on_ctrl_enter)

        self.status_var = tk.StringVar(value="⟳ INITIALIZING...")
        status_label = tk.Label(
            input_card,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            fg=self.sub_text,
            bg=self.card_color
        )
        status_label.pack(anchor="w")

        stats_frame = tk.Frame(main_frame, bg=self.bg_color)
        stats_frame.pack(fill="x", pady=(0, 12))

        self.word_count_var = tk.StringVar(value="WORDS: 0")
        word_count = tk.Label(
            stats_frame,
            textvariable=self.word_count_var,
            font=("Segoe UI", 9, "bold"),
            fg=self.sub_text,
            bg=self.bg_color
        )
        word_count.pack(side="left")

        self.mode_display = tk.Label(
            stats_frame,
            text="MODE: SHORT",
            font=("Segoe UI", 9, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        self.mode_display.pack(side="right")

        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=(0, 12))

        self.play_btn = tk.Button(
            btn_frame,
            text="▶ EXECUTE",
            command=self.on_play_round,
            bg=self.accent_color,
            fg=self.bg_color,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2",
            activebackground=self.accent_dim,
            activeforeground=self.bg_color
        )
        self.play_btn.pack(fill="x")

        settings_card = tk.Frame(
            main_frame,
            bg=self.card_color,
            padx=15,
            pady=12,
            highlightbackground=self.accent_color,
            highlightthickness=1
        )
        settings_card.pack(fill="x")

        mode_label = tk.Label(
            settings_card,
            text="» WORD MODE «",
            font=("Segoe UI", 9, "bold"),
            fg=self.accent_color,
            bg=self.card_color
        )
        mode_label.pack(anchor="w", pady=(0, 8))

        mode_frame = tk.Frame(settings_card, bg=self.card_color)
        mode_frame.pack(fill="x")

        short_radio = tk.Radiobutton(
            mode_frame,
            text="SHORT WORDS",
            variable=self.mode_var,
            value="Short",
            command=self._on_mode_radio,
            bg=self.card_color,
            fg=self.accent_color,
            selectcolor=self.card_color,
            activebackground=self.card_color,
            activeforeground=self.accent_color,
            font=("Segoe UI", 10, "bold")
        )
        short_radio.pack(side="left", padx=(0, 20))

        long_radio = tk.Radiobutton(
            mode_frame,
            text="LONG WORDS",
            variable=self.mode_var,
            value="Long",
            command=self._on_mode_radio,
            bg=self.card_color,
            fg=self.sub_text,
            selectcolor=self.card_color,
            activebackground=self.card_color,
            activeforeground=self.accent_color,
            font=("Segoe UI", 10, "bold")
        )
        long_radio.pack(side="left")

        footer = tk.Frame(main_frame, bg=self.bg_color)
        footer.pack(fill="x", pady=(10, 0))

        version_label = tk.Label(
            footer,
            text=f"◆ v{CURRENT_VERSION} ◆",
            font=("Segoe UI", 8),
            fg=self.sub_text,
            bg=self.bg_color
        )
        version_label.pack(side="left")

        line_label = tk.Label(
            main_frame,
            text="══════════════════════════════════════════════════════════",
            font=("Segoe UI", 8),
            fg=self.accent_color,
            bg=self.bg_color
        )
        line_label.pack(pady=(6, 0))

    def _on_mode_radio(self):
        mode = self.mode_var.get()
        if mode == "Short":
            self.mode_display.config(text="MODE: SHORT")
        else:
            self.mode_display.config(text="MODE: LONG")

    def load_wordlist(self) -> None:
        cache_file = "word_cache.json"
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.wordlist = json.load(f)
                    self.wordlist_loaded = True
                    self.root.after(0, lambda: self.status_var.set(f"✔ {len(self.wordlist)} WORDS LOADED"))
                    return
            except:
                pass
        
        try:
            self.status_var.set("⟳ FETCHING WORD LIST...")
            self.root.update()
            
            url = "https://raw.githubusercontent.com/dwyl/english-words/master/words.txt"
            response = urllib.request.urlopen(url)
            content = response.read().decode('utf-8')
            
            word_list = [w.strip().lower() for w in content.splitlines() if w.strip()]
            self.wordlist = sorted([w for w in word_list if len(w) >= 2 and w.isalpha()])
            
            with open(cache_file, 'w') as f:
                json.dump(self.wordlist, f)
            
            self.wordlist_loaded = True
            self.root.after(0, lambda: self.status_var.set(f"✔ {len(self.wordlist)} WORDS LOADED"))
            
        except Exception as exc:
            self.wordlist_loaded = False
            self.wordlist_error = exc
            self.root.after(0, lambda: self.status_var.set("⚠ FALLBACK MODE ACTIVE"))
            self._load_fallback_words()

    def _load_fallback_words(self) -> None:
        fallback_words = [
            "ability", "across", "action", "active", "actual", "address", "advance", "affect", "agency", "agreement",
            "amount", "animal", "annual", "answer", "appeal", "approach", "around", "arrange", "artistic", "assume",
            "attack", "attempt", "attend", "attract", "author", "balance", "bargain", "bearing", "becoming", "believe",
            "beneath", "benefit", "besides", "better", "beyond", "bitter", "blanket", "bother", "bounce", "branch",
            "breach", "bridge", "briefly", "bright", "broken", "budget", "bullet", "bundle", "burden", "bureau",
            "button", "camera", "cancel", "carbon", "careful", "carry", "center", "chance", "change", "charge",
            "cheap", "cheese", "choice", "choose", "chosen", "circle", "client", "closed", "coffee", "colony",
            "colour", "column", "combat", "comedy", "coming", "common", "comply", "concept", "concern", "conduct",
            "confirm", "conquer", "consent", "consist", "consult", "contain", "content", "contest", "control",
            "cooking", "corner", "county", "couple", "course", "cousin", "create", "credit", "crisis", "custom",
            "damage", "danger", "dealer", "debate", "decade", "defeat", "defend", "define", "degree", "demand",
            "deputy", "derive", "desert", "design", "desire", "detail", "detect", "device", "devote", "differ",
            "direct", "doctor", "domain", "double", "driven", "driver", "during", "easily", "eating", "editor",
            "educate", "effect", "effort", "eighth", "either", "emerge", "empire", "enable", "endure", "energy",
            "engage", "engine", "enough", "ensure", "escape", "estate", "evolve", "examine", "exceed", "except",
            "excuse", "exempt", "expand", "expect", "expert", "export", "expose", "extend", "extent", "fabric",
            "factor", "fairly", "fallen", "farmer", "father", "fellow", "female", "figure", "filter", "finger",
            "finish", "flower", "flying", "follow", "forbid", "forced", "forest", "forget", "formal", "format",
            "former", "father", "foster", "french", "friend", "frozen", "future", "gained", "galaxy", "garden",
            "gather", "gentle", "gently", "gifted", "global", "golden", "govern", "grants", "greater", "ground",
            "grouped", "growing", "guilty", "guitar", "happen", "hardly", "hazard", "health", "heaven", "hidden",
            "holder", "honest", "horror", "humble", "hunter", "ignore", "image", "immune", "impact", "import",
            "impose", "income", "indeed", "indoor", "inform", "injure", "insect", "insert", "inside", "insist",
            "intact", "intend", "intent", "invest", "invest", "jungle", "junior", "killer", "labour", "landed",
            "latter", "launch", "lawyer", "layout", "leader", "league", "lender", "lesson", "letter", "likely",
            "linear", "lively", "living", "lonely", "loving", "luxury", "mainly", "manage", "matter", "medium",
            "member", "memory", "mental", "merely", "method", "middle", "miller", "mining", "minute", "mirror",
            "mobile", "modern", "modest", "moment", "monkey", "motive", "mother", "moving", "murder", "muscle",
            "museum", "mutual", "myself", "namely", "narrow", "nation", "nature", "neither", "neural", "nobody",
            "normal", "notice", "notion", "number", "object", "obtain", "occupy", "offend", "option", "orient",
            "origin", "outfit", "outset", "oxygen", "packed", "partly", "patent", "pattern", "pencil", "people",
            "period", "permit", "person", "phase", "phone", "phrase", "planet", "player", "please", "plenty",
            "pocket", "poetry", "poison", "policy", "polish", "polite", "poorly", "poster", "potato", "powder",
            "powder", "prayer", "prefer", "pretty", "prince", "prison", "profit", "proper", "prove", "public",
            "pursue", "puzzle", "racial", "random", "rarely", "rather", "rating", "reader", "really", "reason",
            "recall", "recent", "record", "reduce", "reform", "region", "regret", "reject", "relate", "relief",
            "remain", "remedy", "remote", "remove", "rental", "repair", "repeat", "report", "rescue", "retain",
            "retire", "return", "reveal", "review", "revolt", "reward", "rising", "robust", "ruling", "running",
            "sacred", "safety", "salary", "sample", "saving", "scheme", "school", "screen", "search", "season",
            "second", "secret", "sector", "secure", "select", "seller", "senior", "serial", "settle", "severe",
            "shadow", "should", "signal", "silent", "silver", "simple", "simply", "single", "skilled", "slave",
            "smooth", "social", "solely", "solve", "source", "speech", "spirit", "spread", "spring", "square",
            "stable", "status", "steady", "stereo", "stolen", "strain", "strand", "stream", "street", "stress",
            "strict", "strike", "string", "strip", "stroke", "strong", "submit", "subtle", "supply", "surely",
            "surface", "surge", "survey", "switch", "symbol", "system", "tackle", "talent", "target", "temple",
            "tender", "terror", "thanks", "theirs", "theory", "thirty", "thorn", "threat", "timber", "tissue",
            "tongue", "toward", "travel", "treaty", "tribal", "trophy", "truly", "twice", "unfair", "unique",
            "unless", "unlike", "update", "useful", "valley", "vanish", "vendor", "victim", "viewer", "virtue",
            "vision", "volume", "wallet", "warmly", "wealth", "weapon", "weekly", "weight", "window", "winter",
            "wisdom", "within", "wonder", "wooden", "worthy", "writer", "yellow", "youth"
        ]
        self.wordlist = sorted(fallback_words)
        self.wordlist_loaded = True
        self.root.after(0, lambda: self.status_var.set(f"✔ {len(self.wordlist)} FALLBACK WORDS"))

    def find_completion(self, prefix: str) -> Optional[str]:
        if not self.wordlist_loaded or not self.wordlist:
            return None

        lower_prefix = prefix.lower()
        candidates: List[str] = []

        for word in self.wordlist:
            if word in self.used_words:
                continue
            if not word.lower().startswith(lower_prefix):
                continue
            if len(word) <= len(prefix):
                continue
            candidates.append(word)

        if not candidates:
            return None

        mode = self.mode_var.get()
        if mode == "Short":
            chosen = min(candidates, key=len)
        else:
            chosen = max(candidates, key=len)

        self.used_words.add(chosen)
        self._update_word_count()
        return chosen[len(prefix):]

    def _update_word_count(self) -> None:
        self.word_count_var.set(f"WORDS: {len(self.used_words)}")

    def _is_roblox_running(self) -> bool:
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(
                ["tasklist"],
                text=True,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return "RobloxPlayerBeta.exe" in output
        except Exception:
            return False

    def _focus_roblox_window(self) -> bool:
        try:
            user32 = ctypes.WinDLL("user32", use_last_error=True)

            titles = ["Roblox", "Roblox Player", "Roblox Game Client"]
            for title in titles:
                hwnd = user32.FindWindowW(None, title)
                if hwnd:
                    if user32.IsIconic(hwnd):
                        user32.ShowWindow(hwnd, 9)
                    user32.SetForegroundWindow(hwnd)
                    user32.BringWindowToTop(hwnd)
                    time.sleep(0.1)
                    return True

            def enum_callback(hwnd, windows):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        if "roblox" in buffer.value.lower():
                            windows.append(hwnd)
                return True

            windows = []
            EnumWindows = user32.EnumWindows
            EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(enum_callback), 0)

            if windows:
                hwnd = windows[0]
                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 9)
                user32.SetForegroundWindow(hwnd)
                user32.BringWindowToTop(hwnd)
                time.sleep(0.1)
                return True

            return False
        except Exception as e:
            print(f"Focus error: {e}")
            return False

    def refresh_roblox_status(self) -> None:
        running = self._is_roblox_running()
        if running:
            self.roblox_status_var.set("ONLINE")
            self.status_dot.config(fg=self.success_color)
        else:
            self.roblox_status_var.set("OFFLINE")
            self.status_dot.config(fg=self.error_color)
        self.root.after(2000, self.refresh_roblox_status)

    def on_play_round(self) -> None:
        prefix = self.prefix_var.get().strip()
        if not prefix:
            messagebox.showwarning("Last Letter Automation", "Please enter starting letters.")
            return

        if not self.wordlist_loaded:
            messagebox.showwarning("Last Letter Automation", "Word list is still loading.")
            return

        completion = self.find_completion(prefix)
        if completion is None:
            messagebox.showinfo("Last Letter Automation", f"No word found starting with '{prefix}'")
            return

        self.root.withdraw()
        self.prefix_var.set("")

        if self._is_roblox_running():
            self.roblox_status_var.set("ONLINE")
            self.status_dot.config(fg=self.success_color)
            self._focus_roblox_window()
        else:
            self.roblox_status_var.set("OFFLINE")
            self.status_dot.config(fg=self.error_color)
            messagebox.showinfo("Last Letter Automation", "Click Roblox window to focus it, then typing will begin.")

        threading.Thread(target=self._type_after_delay, args=(completion,), daemon=True).start()

    def on_ctrl_enter(self, event) -> str:
        self.on_play_round()
        return "break"

    def _type_after_delay(self, completion: str) -> None:
        time.sleep(1.0)

        try:
            delay = 0.01

            for ch in completion:
                keyboard.press_and_release(ch)
                time.sleep(delay)

            keyboard.send("enter")
            time.sleep(1.0)

        except Exception as e:
            print(f"Typing error: {e}")
        finally:
            self.root.after(0, self.root.deiconify)


def main() -> None:
    root = tk.Tk()
    app = LastLetterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
