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


def parse_xml_document(data: bytes) -> List[Keystroke]:
    ledger = ET.fromstring(data)
    if ledger.tag != "ledger":
        raise ValueError("The XML root element must be <ledger>.")

    keystrokes = []
    for entry in ledger:
        if entry.tag != "keystroke":
            raise ValueError("Each child of <ledger> must be a <keystroke>.")
        key = entry.findtext("key")
        timestamp = entry.findtext("timestamp")
        value_text = entry.findtext("ascii_value")
        if key is None or timestamp is None or value_text is None:
            raise ValueError("Each <keystroke> must contain key, timestamp, and ascii_value.")
        try:
            value = int(value_text)
        except ValueError as error:
            raise ValueError("Each ascii_value must be an integer.") from error
        if value < -1 or value > 127:
            raise ValueError("Each ascii_value must be -1 or an ASCII value from 0 to 127.")
        keystrokes.append(Keystroke(key, timestamp, value))
    return keystrokes


def text_from_keystrokes(keystrokes: List[Keystroke]) -> str:
    characters = []
    for keystroke in keystrokes:
        if keystroke.key == "BackSpace" or keystroke.ascii_value == 8:
            if characters:
                characters.pop()
        elif keystroke.ascii_value in (10, 13):
            characters.append("\n")
        elif keystroke.ascii_value == 9:
            characters.append("\t")
        elif 32 <= keystroke.ascii_value <= 126:
            characters.append(chr(keystroke.ascii_value))
    return "".join(characters)


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
        file_menu.add_command(label="Import...", command=self.import_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save As...", command=self.save_as, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        root.configure(menu=menu_bar)
        root.bind("<Control-o>", self.import_file)
        root.bind("<Control-s>", self.save_as)

    def record_keystroke(self, event: tk.Event) -> None:
        self.keystrokes.append(
            Keystroke(
                key=event.keysym,
                timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                ascii_value=ascii_value(event.char),
            )
        )

    def import_file(self, _event: Optional[tk.Event] = None) -> None:
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Import XML ledger",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "rb") as file:
                keystrokes = parse_xml_document(file.read())
        except (OSError, ET.ParseError, ValueError) as error:
            messagebox.showerror(
                "Import failed",
                f"Could not import the XML ledger:\n{error}",
                parent=self.root,
            )
            return

        self.keystrokes = keystrokes
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text_from_keystrokes(keystrokes))
        self.root.title(f"Humanpad - {path}")

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