"""
Last Letter Automation - Neon Edition
A utility for the Roblox Last Letter game
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
        custom_words = [
            "apple", "able", "about", "above", "across", "action", "after", "again", "against", "age",
            "agree", "air", "all", "allow", "almost", "alone", "along", "already", "also", "always",
            "among", "animal", "another", "answer", "any", "anyone", "appear", "area", "arm", "around",
            "arrive", "art", "ask", "back", "ball", "band", "bank", "base", "battle", "beach",
            "bear", "beat", "because", "become", "bed", "before", "begin", "behind", "believe", "best",
            "better", "between", "big", "bird", "black", "blood", "blue", "board", "boat", "body",
            "book", "born", "both", "bottom", "box", "boy", "break", "bring", "brother", "brown",
            "build", "burn", "business", "busy", "call", "camp", "car", "card", "care", "carry",
            "case", "cash", "cat", "catch", "center", "chance", "change", "charge", "child", "choose",
            "city", "class", "clean", "clear", "close", "cloud", "club", "coach", "coast", "color",
            "come", "company", "complete", "computer", "country", "course", "cover", "create", "cross", "crowd",
            "cry", "current", "cut", "dance", "danger", "dark", "date", "day", "dead", "deal",
            "death", "deep", "design", "develop", "die", "differ", "difficult", "direct", "dog", "dollar",
            "door", "down", "draw", "dream", "dress", "drink", "drive", "drop", "drug", "dry",
            "during", "each", "early", "east", "easy", "eat", "economic", "edge", "education", "effect",
            "effort", "eight", "either", "electric", "else", "end", "enemy", "enjoy", "enough", "enter",
            "entire", "equal", "especially", "even", "evening", "event", "ever", "every", "everyone", "example",
            "except", "exist", "expect", "experience", "eye", "face", "fact", "fail", "fall", "family",
            "far", "farm", "fast", "father", "fear", "feel", "feet", "fight", "figure", "fill",
            "final", "find", "fine", "finger", "finish", "fire", "first", "fish", "five", "floor",
            "fly", "follow", "food", "foot", "for", "force", "foreign", "form", "former", "forward",
            "four", "free", "friend", "from", "front", "full", "game", "garden", "general", "get",
            "girl", "give", "glass", "go", "god", "gold", "good", "government", "grand", "great",
            "green", "ground", "group", "grow", "guess", "gun", "guy", "hair", "half", "hand",
            "happen", "happy", "hard", "have", "he", "head", "hear", "heart", "heat", "heavy",
            "help", "her", "here", "high", "history", "hit", "hold", "home", "hope", "horse",
            "hospital", "hot", "hotel", "hour", "house", "how", "however", "huge", "human", "hundred",
            "husband", "idea", "identify", "imagine", "important", "improve", "include", "increase", "indeed", "indicate",
            "individual", "industry", "information", "inside", "instead", "institution", "interest", "into", "investment", "issue",
            "it", "item", "job", "join", "just", "keep", "key", "kid", "kill", "kind",
            "king", "kitchen", "know", "land", "language", "large", "last", "late", "later", "laugh",
            "law", "lay", "lead", "learn", "least", "leave", "left", "less", "let", "letter",
            "level", "life", "light", "like", "line", "list", "listen", "little", "live", "local",
            "long", "look", "lose", "loss", "lot", "love", "low", "machine", "magazine", "main",
            "maintain", "major", "make", "man", "manage", "many", "market", "marriage", "material", "matter",
            "may", "maybe", "mean", "measure", "medical", "meet", "member", "memory", "mention", "message",
            "method", "middle", "might", "military", "million", "mind", "minute", "miss", "mission", "model",
            "modern", "moment", "money", "month", "more", "morning", "most", "mother", "mouth", "move",
            "movement", "movie", "much", "music", "must", "name", "nation", "national", "natural", "nature",
            "near", "nearly", "necessary", "need", "network", "never", "new", "news", "next", "nice",
            "night", "nine", "no", "none", "nor", "north", "not", "note", "nothing", "notice",
            "now", "number", "occur", "off", "offer", "office", "officer", "official", "often", "oil",
            "old", "once", "one", "only", "open", "operation", "opportunity", "option", "order", "organization",
            "other", "our", "out", "outside", "over", "own", "page", "paint", "paper", "parent",
            "part", "participant", "particular", "partner", "party", "pass", "past", "patient", "pattern", "pay",
            "peace", "people", "per", "perform", "perhaps", "period", "person", "personal", "phone", "physical",
            "pick", "picture", "piece", "place", "plan", "plant", "play", "player", "point", "police",
            "policy", "political", "politics", "poor", "popular", "population", "position", "positive", "possible", "power",
            "practice", "prepare", "present", "president", "pressure", "pretty", "prevent", "price", "private", "probably",
            "problem", "process", "produce", "product", "professional", "professor", "program", "project", "property", "protect",
            "prove", "provide", "public", "pull", "purpose", "push", "put", "quality", "question", "quickly",
            "quite", "race", "radio", "raise", "range", "rate", "rather", "reach", "read", "ready",
            "real", "reality", "realize", "really", "reason", "receive", "recent", "recently", "recognize", "record",
            "red", "reduce", "reflect", "region", "relate", "relationship", "religious", "remain", "remember", "remove",
            "report", "represent", "republican", "require", "research", "resource", "respond", "response", "responsibility", "rest",
            "result", "return", "reveal", "rich", "right", "rise", "risk", "road", "rock", "role",
            "room", "rule", "run", "safe", "same", "save", "scene", "school", "science", "scientist",
            "sea", "season", "seat", "second", "section", "security", "see", "seek", "seem", "sell",
            "senior", "sense", "series", "serious", "serve", "service", "set", "seven", "several", "shake",
            "she", "short", "shot", "should", "shoulder", "show", "side", "sign", "significant", "similar",
            "simple", "simply", "since", "sing", "single", "sister", "sit", "site", "situation", "six",
            "size", "skill", "skin", "small", "smile", "social", "society", "soldier", "some", "somebody",
            "someone", "something", "sometimes", "son", "song", "soon", "sort", "sound", "source", "south",
            "southern", "space", "speak", "special", "specific", "speech", "spend", "sport", "spring", "staff",
            "stage", "stand", "standard", "star", "start", "state", "statement", "station", "stay", "step",
            "still", "stock", "stop", "store", "story", "strategy", "street", "strong", "structure", "student",
            "study", "stuff", "style", "subject", "success", "successful", "such", "suddenly", "suffer", "suggest",
            "summer", "support", "sure", "surface", "system", "table", "take", "talk", "task", "tax",
            "teach", "teacher", "team", "technology", "television", "tell", "ten", "tend", "term", "test",
            "than", "that", "the", "their", "them", "themselves", "then", "theory", "there", "these",
            "they", "thing", "think", "third", "this", "those", "though", "thought", "thousand", "threat",
            "three", "through", "throughout", "throw", "thus", "time", "today", "together", "tonight", "too",
            "top", "total", "tough", "toward", "town", "trade", "traditional", "training", "travel", "treat",
            "treatment", "tree", "trial", "trip", "trouble", "true", "truth", "try", "turn", "type",
            "under", "understand", "unit", "until", "up", "upon", "use", "usually", "value", "various",
            "very", "victim", "view", "violence", "visit", "voice", "vote", "wait", "walk", "wall",
            "want", "war", "watch", "water", "way", "we", "weapon", "wear", "week", "weight",
            "well", "west", "western", "what", "whatever", "when", "where", "whether", "which", "while",
            "white", "who", "whole", "whose", "why", "wide", "wife", "will", "win", "wind",
            "window", "wish", "with", "within", "without", "woman", "wonder", "word", "work", "worker",
            "world", "worry", "would", "write", "writer", "wrong", "yard", "yeah", "year", "yes",
            "yet", "you", "young", "your", "yourself"
        ]
        
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
            
            combined = set(word_list)
            combined.update(custom_words)
            
            self.wordlist = sorted([w for w in combined if len(w) >= 2 and w.isalpha()])
            
            with open(cache_file, 'w') as f:
                json.dump(self.wordlist, f)
            
            self.wordlist_loaded = True
            self.root.after(0, lambda: self.status_var.set(f"✔ {len(self.wordlist)} WORDS LOADED"))
            
        except Exception as exc:
            self.wordlist_loaded = True
            self.wordlist = sorted(custom_words)
            self.root.after(0, lambda: self.status_var.set(f"✔ {len(self.wordlist)} CUSTOM WORDS LOADED"))

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
