#!/usr/bin/env python3
"""
Recursively copy a directory tree, converting every .docx to .md via pandoc.
Non-docx files are copied as-is, so you still get images, PDFs, etc.
"""

from pathlib import Path
import shutil, subprocess, sys

# --- CONFIG ---------------------------------------------------------------
SRC  = Path(sys.argv[1]).expanduser().resolve()      # source root
DEST = Path(sys.argv[2]).expanduser().resolve()      # destination root
PANDOC_OPTS = ["--from=docx", "--to=gfm", "-s"]      # tweak if needed
# -------------------------------------------------------------------------

def convert_docx(src_path: Path, dest_path: Path):
    dest_path = dest_path.with_suffix(".md")
    subprocess.run(["pandoc", *PANDOC_OPTS, src_path, "-o", dest_path],
                   check=True)

for path in SRC.rglob("*"):
    rel      = path.relative_to(SRC)
    dest     = DEST / rel
    dest.parent.mkdir(parents=True, exist_ok=True)

    if path.suffix.lower() == ".docx":
        convert_docx(path, dest)          # write .md
    elif path.is_file():
        shutil.copy2(path, dest)          # keep same extension
print(f" Done! Markdown copy lives at:  {DEST}")
