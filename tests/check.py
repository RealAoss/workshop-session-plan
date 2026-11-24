from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import runpy
import tkinter as tk

app = runpy.run_path(str(Path(__file__).resolve().parents[1] / "app.py"))
fields = app["FIELDS"]
sample = ["Saved example"] + [""] * (len(fields) - 1)
assert app["render"](sample) == app["TITLE"] + "\n\n" + fields[0][0] + "\nSaved example"
with TemporaryDirectory() as tmp:
    path = Path(tmp) / "draft.json"
    path.write_text(json.dumps({"project": app["PROJECT"], "sections": sample}), encoding="utf-8")
    assert app["read_draft"](path) == sample
    path.write_text("{}", encoding="utf-8")
    try:
        app["read_draft"](path)
    except ValueError:
        pass
    else:
        raise AssertionError("Wrong draft accepted")

def inspect(window):
    window.update_idletasks()
    assert window.title() == app["TITLE"]
    window.destroy()

with patch.object(tk.Tk, "mainloop", inspect):
    app["main"]()
