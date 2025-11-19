# gui.py
import json
import os
import re
import tempfile
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import tkinter as tk

from .adb_utils import run_adb_command
from .history_manager import load_history, save_history
from urllib.parse import urlparse, urlencode

from .theme import (
    apply_dracula_theme,
    DraculaFrame, DraculaButton, DraculaCheckbutton, DraculaEntry,
    DraculaCombobox, DraculaTreeview, DraculaNotebook,
    DraculaText, DraculaListbox, DraculaLabelFrame,
    DRACULA_BG, DRACULA_FG, DRACULA_GREEN, DRACULA_COMMENT,
    DRACULA_PURPLE, DRACULA_PINK, DRACULA_RED
)

# Применяем тему один раз при импорте


class ManifestGUI:
    def __init__(self, root, parsed_data):
        self.root = root
        self.data = parsed_data
        self.package = parsed_data["package"]
        self.use_adb_prefix = tk.BooleanVar(value=True)
        self.history = load_history(self.package)
        self.component_type_var = tk.StringVar(value="activities")
        self.show_only_exported = tk.BooleanVar(value=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        from .config_manager import load_window_geometry
        saved_geo = load_window_geometry("main", "950x750+100+50")
        self.root.geometry(saved_geo)
        apply_dracula_theme(root)

        self.setup_ui()

        # self.root.update_idletasks()  # ← дождаться инициализации всех виджетов
        # self.on_component_type_change()  # заполнить список
        # if self.history:
        #     self.cmd_combo.set(self.history[0])  # ← не current(), а set()

    def on_closing(self):
        from .config_manager import save_window_geometry
        save_window_geometry("main", self.root.geometry())
        self.root.destroy()

    def setup_ui(self):
        self.root.title("Android Manifest Parser")
        self.notebook = DraculaNotebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_components_tab()
        self.create_info_tab()
        self.create_deeplinks_tab()

    # === COMPONENTS TAB ===
    def create_components_tab(self):
        frame = DraculaFrame(self.notebook)
        self.notebook.add(frame, text="Components")

        top_frame = DraculaFrame(frame)
        top_frame.pack(fill="x", pady=(0, 5))


        types = ["activities", "services", "receivers", "providers"]
        type_menu = ttk.OptionMenu(
            top_frame, self.component_type_var, "activities",*types,
            command=lambda v: self.on_component_type_change(v)
        )
        type_menu.pack(side="left", padx=(0, 10))


        chk_exported = DraculaCheckbutton(
            top_frame, text="Only exported",
            variable=self.show_only_exported,
            command=self.on_component_type_change
        )
        chk_exported.pack(side="left", padx=(0, 10))

        chk_adb = DraculaCheckbutton(
            top_frame, text="ADB prefix",
            variable=self.use_adb_prefix,
            command=self.on_component_select_or_update
        )
        chk_adb.pack(side="left")

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        list_frame = DraculaFrame(paned)
        self.component_listbox = DraculaListbox(list_frame, height=16)
        self.component_listbox.pack(fill="both", expand=True)
        self.component_listbox.bind("<<ListboxSelect>>", self.on_component_select_or_update)
        paned.add(list_frame, weight=1)

        log_frame = DraculaFrame(paned)
        ttk.Label(log_frame, text="Command Log", foreground=DRACULA_COMMENT).pack(anchor="w", padx=2, pady=(0, 2))
        self.log_text = DraculaText(log_frame, height=20, wrap="none")
        scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        paned.add(log_frame, weight=1)

        hist_frame = DraculaFrame(frame)
        hist_frame.pack(fill="x", padx=5, pady=(0, 5))

        ttk.Label(hist_frame, text="Recent intents:", foreground=DRACULA_COMMENT).pack(anchor="w")
        self.cmd_history_var = tk.StringVar()
        self.cmd_combo = DraculaCombobox(
            hist_frame,
            textvariable=self.cmd_history_var,
            values=self.history,
            state="readonly"
        )
        if self.history:
            self.cmd_combo.current(0)
        self.cmd_combo.pack(fill="x", pady=(2, 5))
        self.cmd_combo.bind("<<ComboboxSelected>>", self.on_history_select)

        cmd_frame = DraculaFrame(frame)
        cmd_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.adb_command_var = tk.StringVar()
        cmd_entry = DraculaEntry(cmd_frame, textvariable=self.adb_command_var, width=80)
        cmd_entry.pack(side="left", fill="x", expand=True)

        copy_btn = DraculaButton(cmd_frame, text="Copy", width=7, command=self.copy_current_command)
        copy_btn.pack(side="right", padx=(5, 0))

        run_btn = DraculaButton(cmd_frame, text="Run ADB", width=10, command=self.run_selected_adb)
        run_btn.pack(side="right", padx=(5, 0))

        self.on_component_type_change()

    def on_component_type_change(self, value="activities"):

        print("component type changed called")
        self.component_type_var.set(value)
        self.component_listbox.delete(0, tk.END)
        show_only = self.show_only_exported.get()
        comp_type = self.component_type_var.get()
        for comp in self.data["components"][comp_type]:
            if show_only and not comp["exported"]:
                continue
            mark = "[EXPORTED]" if comp["exported"] else "[NOT EXPORTED]"
            self.component_listbox.insert(tk.END, f"{mark} {comp['class']}")

    def on_component_select_or_update(self, _event=None):
        print("component select or update called")
        idx = self.component_listbox.curselection()
        if not idx:
            return

        typ = self.component_type_var.get()
        visible = [
            c for c in self.data["components"][typ]
            if (not self.show_only_exported.get() or c["exported"])
        ]
        comp = visible[idx[0]]
        pkg = self.data["package"]

        cmd = "# Unsupported component"

        if typ == "activities":
            cname = comp["class"]
            action = next((f["actions"][0] for f in comp["intent_filters"] if f["actions"]), "")
            base = f"am start -n {pkg}/{cname}"
            cmd = base + (f" -a {action}" if action else "")

        elif typ == "services":
            cname = comp["class"]
            action = next((f["actions"][0] for f in comp["intent_filters"] if f["actions"]), "")
            base = f"am start-service -n {pkg}/{cname}"
            cmd = base + (f" -a {action}" if action else "")

        elif typ == "receivers":
            cname = comp["class"]
            action = next((f["actions"][0] for f in comp["intent_filters"] if f["actions"]), "")
            cmd = f"am broadcast -n {pkg}/{cname}" + (f" -a {action}" if action else "")

        elif typ == "providers":
            authority = comp.get("authority")
            if authority:
                cmd = f"content query --uri content://{authority}"
            else:
                cmd = "# Provider has no authority"

        if self.use_adb_prefix.get():
            cmd = f"adb shell {cmd}"

        self.adb_command_var.set(cmd)

    def on_history_select(self, _event=None):
        raw = self.cmd_history_var.get()
        if not self.use_adb_prefix.get() and raw.startswith("adb shell "):
            cmd = raw[10:]
        elif self.use_adb_prefix.get() and not raw.startswith("adb shell "):
            cmd = f"adb shell {raw}"
        else:
            cmd = raw
        self.adb_command_var.set(cmd)

    def run_selected_adb(self):
        full_cmd = self.adb_command_var.get().strip()
        if not full_cmd or full_cmd.startswith("#"):
            self.log_command(full_cmd or "<empty>", error="No valid command")
            return

        clean = full_cmd
        if clean.startswith("adb shell "):
            clean = clean[10:]
        elif clean.startswith("adb "):
            clean = clean[4:]
        args = "shell " + clean

        try:
            out = run_adb_command(args)
            if full_cmd not in self.history:
                self.history.append(full_cmd)
                save_history(self.package, self.history)
                self.cmd_combo["values"] = self.history
                self.cmd_combo.current(len(self.history) - 1)
            self.log_command(full_cmd, output=out)
        except Exception as e:
            self.log_command(full_cmd, error=str(e))

    def log_command(self, cmd: str, output: str = "", error: str = ""):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{ts}] {cmd.strip()}"
        line = f"{prefix}\n→ ❌ {error}\n\n" if error else f"{prefix}\n→ ✅ {output or 'Success'}\n\n"
        self.log_text.insert("end", line)
        self.log_text.see("end")

    def copy_current_command(self):
        cmd = self.adb_command_var.get().strip()
        if cmd and not cmd.startswith("#"):
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd)
            self.root.bell()
        else:
            messagebox.showinfo("Info", "No valid command to copy")

    # === INFO TAB ===
    def create_info_tab(self):
        frame = DraculaFrame(self.notebook)
        self.notebook.add(frame, text="Info")

        info_text = DraculaText(frame, wrap="word", height=25)
        info_text.pack(fill="both", expand=True, padx=5, pady=5)

        content = [
            f"Package: {self.data['package']}",
            f"Application class: {self.data['application_class'] or 'None'}",
            f"minSdkVersion: {self.data['min_sdk'] or 'N/A'}",
            f"targetSdkVersion: {self.data['target_sdk'] or 'N/A'}\n",
            "Dangerous Permissions:"
        ]
        for p in self.data["permissions"]:
            if p["dangerous"]:
                content.append(f"  🔒 {p['name']}")
        content.append("\nAll Permissions:")
        for p in self.data["permissions"]:
            icon = "⚠️" if p["dangerous"] else "✅"
            content.append(f"  {icon} {p['name']}")
        content.append("\nQueries (declared packages/intents):")
        content.extend(f"  • {q}" for q in self.data["queries"])

        info_text.insert("1.0", "\n".join(content))
        info_text.config(state="normal")

        copy_btn = DraculaButton(
            frame, text="Copy to Clipboard",
            command=lambda: self.root.clipboard_append(info_text.get("1.0", "end-1c"))
        )
        copy_btn.pack(pady=5)

    # === DEEPLINKS TAB ===
    def create_deeplinks_tab(self):
        frame = DraculaFrame(self.notebook)
        self.notebook.add(frame, text="Deeplinks")

        from .payload_manager import load_payloads
        self.payloads = load_payloads(self.package)

        top_frame = DraculaFrame(frame)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.use_endpoints = tk.BooleanVar(value=True)
        self.use_query = tk.BooleanVar(value=True)
        self.combine_all = tk.BooleanVar(value=True)

        DraculaCheckbutton(top_frame, text="Endpoints", variable=self.use_endpoints,
                           command=self.preview_html).pack(side="left", padx=(0, 10))
        DraculaCheckbutton(top_frame, text="Query params", variable=self.use_query,
                           command=self.preview_html).pack(side="left", padx=(0, 10))
        DraculaCheckbutton(top_frame, text="All combinations", variable=self.combine_all,
                           command=self.preview_html).pack(side="left", padx=(0, 10))
        DraculaButton(top_frame, text="🔄 Generate HTML", command=self.generate_html_and_preview).pack(side="right")

        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        ep_frame = DraculaLabelFrame(paned, text="Endpoints", padding=5)
        self.ep_listbox = DraculaListbox(ep_frame, height=8, selectmode=tk.EXTENDED)
        self.ep_listbox.pack(fill="both", expand=True, pady=(0, 5))
        btn_ep = DraculaFrame(ep_frame)
        DraculaButton(btn_ep, text="+", width=3, command=self.add_endpoint).pack(side="left")
        DraculaButton(btn_ep, text="-", width=3, command=self.remove_endpoint).pack(side="left")
        btn_ep.pack()
        paned.add(ep_frame, weight=1)

        qp_frame = DraculaLabelFrame(paned, text="Query Params", padding=5)
        self.qp_tree = DraculaTreeview(qp_frame, columns=("name", "value"), show="headings", height=8)
        self.qp_tree.heading("name", text="Name")
        self.qp_tree.heading("value", text="Value")
        self.qp_tree.column("name", width=100)
        self.qp_tree.column("value", width=120)
        self.qp_tree.pack(fill="both", expand=True, pady=(0, 5))
        btn_qp = DraculaFrame(qp_frame)
        DraculaButton(btn_qp, text="+", width=3, command=self.add_param).pack(side="left")
        DraculaButton(btn_qp, text="-", width=3, command=self.remove_param).pack(side="left")
        btn_qp.pack()
        paned.add(qp_frame, weight=1)

        filter_frame = DraculaLabelFrame(frame, text="🚫 Exclusion Filters", padding=5)
        filter_frame.pack(fill="x", padx=10, pady=5)

        cols = ("pattern", "enabled", "invert", "case", "auto")
        self.filter_tree = DraculaTreeview(filter_frame, columns=cols, show="headings", height=5)
        for col, text in zip(cols, ["Pattern", "✓", "¬", "Aa", "Auto-*"]):
            self.filter_tree.heading(col, text=text)
            self.filter_tree.column(col, anchor="center", width=60 if col != "pattern" else 300)
        self.filter_tree.column("pattern", anchor="w")
        self.filter_tree.pack(fill="x", pady=(0, 5))
        self.filter_tree.bind("<Button-1>", self.toggle_filter_column)

        btn_f = DraculaFrame(filter_frame)
        DraculaButton(btn_f, text="+", width=3, command=self.add_exclude_pattern).pack(side="left")
        DraculaButton(btn_f, text="-", width=3, command=self.remove_exclude_pattern).pack(side="left")
        DraculaButton(btn_f, text="Test", command=self.test_filters).pack(side="left", padx=(10, 0))
        ttk.Label(btn_f, text="Matching URLs:", foreground=DRACULA_COMMENT).pack(side="left", padx=(10, 0))
        self.match_count_var = tk.StringVar(value="0")
        ttk.Label(btn_f, textvariable=self.match_count_var, foreground=DRACULA_GREEN).pack(side="left")
        btn_f.pack()

        html_frame = DraculaLabelFrame(frame, text="HTML Preview", padding=5)
        html_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.deeplink_text = DraculaText(html_frame, wrap="none", height=15)
        scroll = ttk.Scrollbar(html_frame, orient="vertical", command=self.deeplink_text.yview)
        self.deeplink_text.configure(yscrollcommand=scroll.set)
        self.deeplink_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        btns = DraculaFrame(frame)
        btns.pack(pady=5)
        DraculaButton(btns, text="💾 Save Payloads", command=self.save_payloads).pack(side="left", padx=5)
        DraculaButton(btns, text="📤 Save HTML", command=self.save_html).pack(side="left", padx=5)
        DraculaButton(btns, text="📂 Load Payloads", command=self.load_payloads_from_file).pack(side="left", padx=5)
        DraculaButton(btns, text="📤 Push to Device", command=self.push_html_to_device).pack(side="left", padx=5)
        DraculaButton(btns, text="📱 Open on Device", command=self.open_html_on_device).pack(side="left", padx=5)

        self.load_payloads_into_ui()
        self.preview_html()

    # === Deeplinks: UI helpers ===
    def load_payloads_into_ui(self):
        try:
            self.ep_listbox.delete(0, tk.END)
            for ep in self.payloads.get("endpoints", ["/"]):
                self.ep_listbox.insert(tk.END, ep)

            for item in self.qp_tree.get_children():
                self.qp_tree.delete(item)
            for p in self.payloads.get("query_params", []):
                self.qp_tree.insert("", "end", values=(p["name"], p["value"]))
        except Exception as e:
            print(f"[GUI] Failed to load payloads: {e}")

    def add_endpoint(self):
        ep = simpledialog.askstring("Add Endpoint", "Enter endpoint (e.g. /test or /api/v1/):", parent=self.root)
        if ep:
            self.ep_listbox.insert(tk.END, ep.strip() or "/")

    def remove_endpoint(self):
        for i in reversed(self.ep_listbox.curselection()):
            self.ep_listbox.delete(i)

    def add_param(self):
        name = simpledialog.askstring("Param Name", "Name:", parent=self.root)
        if name is None:
            return
        value = simpledialog.askstring("Param Value", f"Value for '{name}':", parent=self.root)
        if value is not None:
            self.qp_tree.insert("", "end", values=(name.strip(), value.strip()))

    def remove_param(self):
        for item in self.qp_tree.selection():
            self.qp_tree.delete(item)

    def save_payloads(self):
        endpoints = [self.ep_listbox.get(i) for i in range(self.ep_listbox.size())]
        params = [{"name": self.qp_tree.item(i, "values")[0],
                   "value": self.qp_tree.item(i, "values")[1]}
                  for i in self.qp_tree.get_children()]

        data = {"endpoints": endpoints, "query_params": params}
        from .payload_manager import save_payloads
        path = save_payloads(self.package, data)
        messagebox.showinfo("Saved", f"Payloads saved to:\n{os.path.basename(path)}")

    def load_payloads_from_file(self):
        filepath = filedialog.askopenfilename(
            title="Load Payloads JSON",
            filetypes=[("JSON files", "*.json")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            endpoints = [str(ep).strip() or "/" for ep in data.get("endpoints", [])]
            params = []
            for p in data.get("query_params", []):
                if isinstance(p, dict) and p.get("name"):
                    name = str(p["name"]).strip()
                    val = str(p.get("value", "")).strip()
                    if name:
                        params.append((name, val))

            self.ep_listbox.delete(0, tk.END)
            for ep in endpoints:
                self.ep_listbox.insert(tk.END, ep)

            for item in self.qp_tree.get_children():
                self.qp_tree.delete(item)
            for name, val in params:
                self.qp_tree.insert("", "end", values=(name, val))

            self.preview_html()
            messagebox.showinfo("Success", f"Loaded from {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed: {e}")

    def preview_html(self):
        try:
            endpoints = [self.ep_listbox.get(i) for i in range(self.ep_listbox.size())]
            params = []
            for item in self.qp_tree.get_children():
                name, val = self.qp_tree.item(item, "values")
                params.append((name, val))

            base_urls = self.data["deeplinks"] + self.data["applinks"]
            from .deeplink_generator import generate_intruder_html
            html = generate_intruder_html(
                base_urls=base_urls,
                endpoints=endpoints if self.use_endpoints.get() else [],
                query_params=params if self.use_query.get() else [],
                combine_all=self.combine_all.get()
            )
            self.deeplink_text.delete("1.0", tk.END)
            self.deeplink_text.insert("1.0", html)
        except Exception as e:
            print(f"[Preview Error] {e}")

    def generate_html_and_preview(self):
        try:
            endpoints = [self.ep_listbox.get(i) for i in range(self.ep_listbox.size())]
            params = []
            for item in self.qp_tree.get_children():
                name, val = self.qp_tree.item(item, "values")
                params.append((name, val))

            base_urls = self.data["deeplinks"] + self.data["applinks"]
            from .deeplink_generator import generate_intruder_html
            html = generate_intruder_html(
                base_urls=base_urls,
                endpoints=endpoints if self.use_endpoints.get() else [],
                query_params=params if self.use_query.get() else [],
                combine_all=self.combine_all.get()
            )

            # Извлекаем ссылки и фильтруем
            import re
            urls = re.findall(r'href="([^"]+)"', html)
            urls = list(dict.fromkeys(urls))
            filtered = [u for u in urls if not self.should_exclude_url(u)]

            links = "\n".join(f'<a href="{u}">{u}</a><br>' for u in sorted(filtered))
            final_html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Filtered Payloads</title>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Consolas, monospace; background: #282a36; color: #50fa7b; padding: 20px; }}
    a {{ color: #bd93f9; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
<h2>Filtered Payloads ({len(filtered)}):</h2>
{links}
</body>
</html>"""
            self.deeplink_text.delete("1.0", tk.END)
            self.deeplink_text.insert("1.0", final_html)
        except Exception as e:
            import traceback
            messagebox.showerror("Error", f"{e}\n\n{traceback.format_exc()}")

    def should_exclude_url(self, url: str) -> bool:
        for item in self.filter_tree.get_children():
            pat, en, inv, cs, ae = self.filter_tree.item(item, "values")
            if en != "✓" or not pat:
                continue
            try:
                pattern = re.escape(pat).replace(r'\*', '.*').replace(r'\?', '.') if ae == "✓" else pat
                flags = 0 if cs == "✓" else re.IGNORECASE
                matched = bool(re.search(pattern, url, flags))
                if inv == "✓":
                    matched = not matched
                if matched:
                    return True
            except re.error:
                continue
        return False

    def test_filters(self):
        base_urls = self.data["deeplinks"] + self.data["applinks"]
        endpoints = [self.ep_listbox.get(i) for i in range(self.ep_listbox.size())]
        params = []
        for item in self.qp_tree.get_children():
            name, val = self.qp_tree.item(item, "values")
            params.append((name, val))

        candidates = set(base_urls)
        for url in base_urls:
            if url.startswith(("http://", "https://")):
                parsed = urlparse(url)
                clean = f"{parsed.scheme}://{parsed.netloc}"
                for ep in endpoints or ["/"]:
                    ep = "/" + ep.lstrip("/")
                    candidates.add(f"{clean}{ep}")
                if params:
                    qs = urlencode(params)
                    candidates.add(f"{clean}{parsed.path}?{qs}")

        count = sum(1 for u in candidates if self.should_exclude_url(u))
        self.match_count_var.set(str(count))

    def add_exclude_pattern(self):
        pat = simpledialog.askstring("Add Pattern", "e.g. *\\.tj, https://global*", parent=self.root)
        if pat:
            self.filter_tree.insert("", "end", values=(pat, "✓", "", "", "✓"))

    def remove_exclude_pattern(self):
        for item in self.filter_tree.selection():
            self.filter_tree.delete(item)

    def toggle_filter_column(self, event):
        region = self.filter_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = self.filter_tree.identify_column(event.x)
        row = self.filter_tree.identify_row(event.y)
        if not row or col not in ("#2", "#3", "#4", "#5"):
            return
        idx = {"#2": 1, "#3": 2, "#4": 3, "#5": 4}[col]
        vals = list(self.filter_tree.item(row, "values"))
        vals[idx] = "✓" if vals[idx] == "" else ""
        self.filter_tree.item(row, values=vals)

    # === File / Device Ops ===
    def save_html(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")],
            initialfile=f"{self.package}_payloads.html"
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.deeplink_text.get("1.0", "end-1c"))
            messagebox.showinfo("Success", "HTML saved!")

    def push_html_to_device(self):
        html = self.deeplink_text.get("1.0", "end-1c").strip()
        if not html:
            messagebox.showwarning("Empty", "HTML preview is empty")
            return

        filename = f"{self.package}_payloads.html"
        device_path = f"/sdcard/Download/{filename}"
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
                tmp.write(html)
                tmp_path = tmp.name
            run_adb_command(f"push {tmp_path} {device_path}")
            self.log_command(f"adb push ...", output=f"✓ Pushed to {device_path}")
            self.last_pushed_html_path = device_path
            messagebox.showinfo("Success", f"Pushed to:\n{device_path}")
        except Exception as e:
            self.log_command("push", error=str(e))
            messagebox.showerror("ADB Error", f"Push failed:\n{e}")
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def open_html_on_device(self):
        path = getattr(self, "last_pushed_html_path", f"/sdcard/Download/{self.package}_payloads.html")
        try:
            import base64
            html = self.deeplink_text.get("1.0", "end-1c").strip()
            encoded = base64.b64encode(html.encode("utf-8")).decode()
            uri = f"text/html;base64,{encoded}"
            cmd = f'shell am start -a android.intent.action.VIEW -d "{uri}"'
            run_adb_command(cmd)
            self.log_command("open via data URI", output="✓ Opened in browser")
            messagebox.showinfo("Success", "Opened in default browser")
        except Exception as e:
            self.log_command("open", error=str(e))
            messagebox.showerror("Open Error", f"{e}")