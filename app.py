"""Edit, save and export a structured document locally."""
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

TITLE = 'Workshop Session Plan'
PROJECT = 'workshop-session-plan'
FIELDS = [('Workshop and audience', 'Intro to spreadsheets · first-time users'),
 ('Learning outcome', 'Participants can filter a table by one column.'),
 ('Materials', 'One example file per person.'),
 ('Timed activities', '10 min demo, 15 min practice, 5 min debrief.'),
 ('Check for understanding', 'Ask participants to filter a second table independently.')]


def render(values):
    sections = [f"{label}\n{value.strip()}" for (label, _), value in zip(FIELDS, values, strict=True) if value.strip()]
    return TITLE + "\n\n" + "\n\n".join(sections) if sections else ""


def read_draft(path):
    draft = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(draft, dict) or draft.get("project") != PROJECT:
        raise ValueError("This draft belongs to another application.")
    values = draft.get("sections")
    if not isinstance(values, list) or len(values) != len(FIELDS) or not all(isinstance(s, str) for s in values):
        raise ValueError("The draft has invalid section data.")
    return values


def main():
    window = tk.Tk()
    window.title(TITLE)
    window.geometry("870x660")
    frame = ttk.Frame(window, padding=12)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text=TITLE, font=("TkDefaultFont", 19, "bold")).pack(anchor="w")
    tabs = ttk.Notebook(frame)
    tabs.pack(fill="both", expand=True, pady=8)
    form, report = ttk.Frame(tabs), ttk.Frame(tabs)
    tabs.add(form, text="Edit")
    tabs.add(report, text="Preview")
    preview = ScrolledText(report, wrap="word", state="disabled")
    preview.pack(fill="both", expand=True)
    editors = []
    for i, (label, example) in enumerate(FIELDS):
        ttk.Label(form, text=label).grid(row=2*i, column=0, sticky="w")
        editor = ScrolledText(form, height=2, wrap="word", undo=True)
        editor.grid(row=2*i+1, column=0, sticky="nsew", pady=(0, 5))
        form.rowconfigure(2*i+1, weight=1)
        editor.insert("1.0", example)
        editors.append(editor)
    form.columnconfigure(0, weight=1)

    def values():
        return [editor.get("1.0", "end-1c") for editor in editors]

    def update(event=None):
        preview.configure(state="normal")
        preview.delete("1.0", "end")
        preview.insert("1.0", render(values()))
        preview.configure(state="disabled")

    def load():
        name = filedialog.askopenfilename(filetypes=[("Draft", "*.json")])
        if not name:
            return
        try:
            restored = read_draft(name)
            for editor, value in zip(editors, restored):
                editor.delete("1.0", "end")
                editor.insert("1.0", value)
            update()
        except (OSError, ValueError) as error:
            messagebox.showerror("Could not open draft", str(error))

    def save(draft):
        content = json.dumps({"project": PROJECT, "sections": values()}, ensure_ascii=False, indent=2) if draft else render(values())
        if not content:
            messagebox.showinfo(TITLE, "Fill in at least one section.")
            return
        ext = ".json" if draft else ".txt"
        name = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[("Draft" if draft else "Text document", "*"+ext)])
        if name:
            try:
                Path(name).write_text(content, encoding="utf-8")
            except OSError as error:
                messagebox.showerror("Could not save file", str(error))
    tabs.bind("<<NotebookTabChanged>>", update)
    bar = ttk.Frame(frame)
    bar.pack(fill="x")
    for label, action in [("Open draft", load), ("Save draft", lambda: save(True)), ("Export text", lambda: save(False))]:
        ttk.Button(bar, text=label, command=action).pack(side="left", padx=3)
    window.mainloop()


if __name__ == "__main__":
    main()
