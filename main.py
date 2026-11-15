#!/usr/bin/env python3
"""Humanpad text editor, saves as XML."""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional
import xml.etree.ElementTree as ET


def xml_document(text: str) -> bytes:
    document = ET.Element("document")
    content = ET.SubElement(document, "content")
    content.text = text
    return ET.tostring(document, encoding="utf-8", xml_declaration=True)


class Humanpad:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Humanpad")
        self.root.geometry("700x500")

        self.text = tk.Text(root, wrap="word", undo=True)
        scrollbar = tk.Scrollbar(root, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Save As...", command=self.save_as, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        root.configure(menu=menu_bar)
        root.bind("<Control-s>", self.save_as)

    def save_as(self, _event: Optional[tk.Event] = None) -> None:
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save as XML",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "wb") as file:
                file.write(xml_document(self.text.get("1.0", "end-1c")))
        except OSError as error:
            messagebox.showerror("Save failed", f"Could not save the file:\n{error}", parent=self.root)
            return

        self.root.title(f"Humanpad - {path}")


def main() -> None:
    root = tk.Tk()
    Humanpad(root)
    root.mainloop()


if __name__ == "__main__":
    main()