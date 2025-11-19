# main.py
import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from .parser import parse_manifest
from .gui import ManifestGUI

from xml.etree import ElementTree as ET
import tempfile

def is_valid_manifest_xml(text: str) -> bool:
    try:
        root = ET.fromstring(text.strip())
        return root.tag == "manifest" and "package" in root.attrib
    except ET.ParseError:
        return False

def get_manifest_from_dialog():

    from .config_manager import load_window_geometry, save_window_geometry
    root = tk.Tk()
    root.title("Select Manifest Source")
    root.resizable(True, True)

    saved_geo = load_window_geometry("chooser", "400x180+300+300")
    root.geometry(saved_geo)

    result = {"content": None, "source": None}
    root_destroyed = False

    def safe_destroy():
        nonlocal root_destroyed
        if not root_destroyed:
            try:
                save_window_geometry("chooser", root.geometry())
            except:
                pass
            root.destroy()
            root_destroyed = True

    def use_file():
        path = filedialog.askopenfilename(
            title="Select AndroidManifest.xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    result["content"] = f.read()
                result["source"] = path
                safe_destroy()
                root.quit()
            except Exception as e:
                messagebox.showerror("Read Error", f"Cannot read file:\n{e}")

    def use_clipboard():
        try:
            clipboard = root.clipboard_get()
        except tk.TclError:
            messagebox.showwarning("Clipboard Empty", "Clipboard is empty or contains non-text data.")
            return

        if is_valid_manifest_xml(clipboard):
            result["content"] = clipboard
            result["source"] = "clipboard"
            safe_destroy()
            root.quit()
        else:
            messagebox.showerror("Invalid XML", "Clipboard does not contain a valid AndroidManifest.xml")

    # --- Dracula-стилизованный UI ---
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(
        main_frame,
        text="How to load the manifest?",
        font=("Consolas", 11)
    ).pack(pady=(0, 15))

    btn_frame = tk.Frame(main_frame)
    btn_frame.pack()

    tk.Button(btn_frame, text="📁 Choose File", command=use_file, width=20).pack(pady=5)
    tk.Button(btn_frame, text="📋 Paste from Clipboard", command=use_clipboard, width=20).pack(pady=5)

    tk.Label(
        main_frame,
        text="Hint: Copy full <manifest>...</manifest> XML",
        font=("Consolas", 8)
    ).pack(pady=(15, 0))

    # root.mainloop()
    main_frame.mainloop()
    return result["content"], result["source"]

def parse_from_file_or_string(input_data):
    """Принимает путь к файлу или XML-строку. Возвращает parsed_data."""
    try:
        if os.path.isfile(input_data):
            return parse_manifest(input_data)
        else:
            # Считаем, что это XML-строка
            with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False, encoding="utf-8") as tmp:
                tmp.write(input_data)
                tmp_path = tmp.name
            try:
                return parse_manifest(tmp_path)
            finally:
                os.unlink(tmp_path)
    except Exception as e:
        raise RuntimeError(f"Failed to parse manifest: {e}")


def main():
    xml_content = None

    # 🔹 1. Если передан аргумент — пробуем прочитать файл
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            try:
                with open(arg, "r", encoding="utf-8") as f:
                    xml_content = f.read()
                source_desc = arg
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file:\n{e}")
                return
        else:
            # Может, это валидный XML? (редко, но вдруг)
            if is_valid_manifest_xml(arg):
                xml_content = arg
                source_desc = "argument (XML string)"
            else:
                messagebox.showerror("Error", f"Not a file and not valid XML:\n{arg}")
                return

    # 🔹 2. Если ничего не получили — показываем диалог
    if xml_content is None:
        xml_content, source_desc = get_manifest_from_dialog()
        if not xml_content:
            print("No manifest source selected. Exiting.")
            return

    # 🔹 3. Парсим
    try:
        data = parse_from_file_or_string(xml_content)
    except Exception as e:
        messagebox.showerror("Parse Error", str(e))
        return

    # 🔹 4. Запуск GUI
    root = tk.Tk()
    app = ManifestGUI(root, data)
    root.mainloop()


if __name__ == "__main__":
    main()

