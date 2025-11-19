# theme.py
import tkinter as tk
from tkinter import ttk

# Цвета Dracula
DRACULA_BG = "#282a36"
DRACULA_FG = "#f8f8f2"
DRACULA_GREEN = "#50fa7b"
DRACULA_COMMENT = "#6272a4"
DRACULA_PURPLE = "#bd93f9"
DRACULA_PINK = "#ff79c6"
DRACULA_RED = "#ff5555"


def apply_dracula_theme(root):
    style = ttk.Style(root)
    style.theme_use("default")

    # Общие настройки
    style.configure("TFrame", background=DRACULA_BG)
    style.configure("TLabel", background=DRACULA_BG, foreground=DRACULA_FG)
    style.configure("TButton",
                    background=DRACULA_PURPLE, foreground=DRACULA_BG,
                    font=("Consolas", 10), padding=4)
    style.map("TButton",
              background=[("active", DRACULA_PINK)],
              foreground=[("active", DRACULA_BG)])

    style.configure("TCheckbutton",
                    background=DRACULA_BG, foreground=DRACULA_FG,
                    font=("Consolas", 10))
    style.map("TCheckbutton",
              background=[("active", DRACULA_BG)])

    style.configure("TEntry",
                    fieldbackground=DRACULA_BG, foreground=DRACULA_GREEN,
                    insertcolor=DRACULA_FG)

    style.configure("TCombobox",
                    fieldbackground=DRACULA_BG, foreground=DRACULA_GREEN,
                    insertcolor=DRACULA_FG)
    style.map("TCombobox",
              fieldbackground=[("readonly", DRACULA_BG)],
              selectbackground=[("readonly", DRACULA_PURPLE)],
              selectforeground=[("readonly", DRACULA_BG)])

    style.configure("Treeview",
                    background=DRACULA_BG, foreground=DRACULA_GREEN,
                    fieldbackground=DRACULA_BG)
    style.map("Treeview",
              background=[("selected", DRACULA_PURPLE)],
              foreground=[("selected", DRACULA_BG)])
    style.configure("Treeview.Heading",
                    background=DRACULA_COMMENT, foreground=DRACULA_FG)

    style.configure("TNotebook", background=DRACULA_BG, borderwidth=0)
    style.configure("TNotebook.Tab", padding=[12, 6])
    style.map("TNotebook.Tab",
              background=[("selected", DRACULA_COMMENT), ("!selected", DRACULA_BG)],
              foreground=[("selected", DRACULA_FG), ("!selected", DRACULA_COMMENT)])

    style.configure("TLabelframe", background=DRACULA_BG, foreground=DRACULA_COMMENT)
    style.configure("TLabelframe.Label", background=DRACULA_BG, foreground=DRACULA_COMMENT)


# === Dracula-виджеты ===

class DraculaFrame(ttk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("style", "TFrame")
        super().__init__(parent, **kw)


class DraculaButton(ttk.Button):
    def __init__(self, parent, **kw):
        kw.setdefault("style", "TButton")
        super().__init__(parent, **kw)


class DraculaCheckbutton(ttk.Checkbutton):
    def __init__(self, parent, **kw):
        kw.setdefault("style", "TCheckbutton")
        super().__init__(parent, **kw)


class DraculaEntry(ttk.Entry):
    def __init__(self, parent, **kw):
        kw.setdefault("style", "TEntry")
        super().__init__(parent, **kw)


class DraculaCombobox(ttk.Combobox):
    def __init__(self, parent, **kw):
        kw.setdefault("style", "TCombobox")
        super().__init__(parent, **kw)


class DraculaTreeview(ttk.Treeview):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)


class DraculaNotebook(ttk.Notebook):
    def __init__(self, parent, **kw):
        kw.setdefault("style", "TNotebook")
        super().__init__(parent, **kw)


class DraculaLabelFrame(ttk.Labelframe):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)


# === NON-TTK виджеты (требуют ручной стилизации) ===

class DraculaListbox(tk.Listbox):
    def __init__(self, parent, **kw):
        defaults = {
            "bg": DRACULA_BG,
            "fg": DRACULA_GREEN,
            "selectbackground": DRACULA_PURPLE,
            "selectforeground": DRACULA_BG,
            "font": ("Consolas", 10),
            "highlightbackground": DRACULA_COMMENT,
            "highlightcolor": DRACULA_PURPLE,
            "highlightthickness": 1,
            "borderwidth": 0,
        }
        defaults.update(kw)
        super().__init__(parent, **defaults)


class DraculaText(tk.Text):
    def __init__(self, parent, **kw):
        defaults = {
            "bg": DRACULA_BG,
            "fg": DRACULA_GREEN,
            "insertbackground": DRACULA_FG,
            "selectbackground": DRACULA_PURPLE,
            "selectforeground": DRACULA_BG,
            "highlightbackground": DRACULA_COMMENT,
            "highlightcolor": DRACULA_PURPLE,
            "highlightthickness": 1,
            "borderwidth": 0,
            "font": ("Consolas", 10),
        }
        defaults.update(kw)
        super().__init__(parent, **defaults)

class DraculaLabel(ttk.Label):
    def __init__(self, parent, **kw):
        kw.setdefault("background", DRACULA_BG)
        kw.setdefault("foreground", DRACULA_FG)
        super().__init__(parent, **kw)