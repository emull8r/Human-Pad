#!/usr/bin/env python3
"""Humanpad text editor, saves as XML."""

import tkinter as tk
from tkinter import filedialog, messagebox
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Keystroke:
    key: str
    timestamp: str
    ascii_value: int


def ascii_value(character: str) -> int:
    if len(character) == 1 and ord(character) <= 127:
        return ord(character)
    return -1


def xml_document(keystrokes: List[Keystroke]) -> bytes:
    ledger = ET.Element("ledger")
    for keystroke in keystrokes:
        entry = ET.SubElement(ledger, "keystroke")
        ET.SubElement(entry, "key").text = keystroke.key
        ET.SubElement(entry, "timestamp").text = keystroke.timestamp
        ET.SubElement(entry, "ascii_value").text = str(keystroke.ascii_value)
    return ET.tostring(ledger, encoding="utf-8", xml_declaration=True)


class Humanpad:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Humanpad")
        self.root.geometry("700x500")
        self.keystrokes: List[Keystroke] = []

        self.text = tk.Text(root, wrap="word", undo=True)
        self.text.bind("<KeyPress>", self.record_keystroke, add="+")
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

    def record_keystroke(self, event: tk.Event) -> None:
        self.keystrokes.append(
            Keystroke(
                key=event.keysym,
                timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                ascii_value=ascii_value(event.char),
            )
        )

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
                file.write(xml_document(self.keystrokes))
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