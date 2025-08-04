from __future__ import annotations

#!/usr/bin/env python
"""
0x1  STS_NEEDSUPLOAD         waiting to upload
0x2  STS_NEEDSDOWNLOAD       waiting to download
0x4  STS_TRANSFERRING        actively moving data
0x8  STS_PAUSED              paused/stalled
0x10 STS_HASERROR            last try failed
0x200 STS_INCOMPLETE         truncated placeholder
"""

#!/usr/bin/env python
"""
icloud_resync_needupload.py
---------------------------
Force-re-submit iCloud-for-Windows files whose
System.SyncTransferStatusFlags == 3 (0x1 | 0x2).

Usage
-----
    python icloud_resync_needupload.py                # auto-detect default folder
    python icloud_resync_needupload.py "D:\\iCloud"   # explicit path

Requirements
------------
    pip install pywin32     # only external dependency
"""

import hashlib
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# ── logging ────────────────────────────────────────────────────────────────────
LOG_FILE = "icloud_resync.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("icloud_fix")

# ── COM helpers (pywin32) ──────────────────────────────────────────────────────
import pythoncom
from win32com.propsys import propsys, pscon

GPS_DEFAULT = getattr(pscon, "GPS_DEFAULT", 0)
PK_SYNCFLAGS = propsys.PSGetPropertyKeyFromName("System.SyncTransferStatusFlags")
TARGET_FLAG_VALUE = 0x8  # STS_NEEDSUPLOAD | STS_NEEDSDOWNLOAD -- sometimes you can use 8 (paused)

def get_sync_flags(path: Path) -> int:
    """Return System.SyncTransferStatusFlags (int) or 0 if missing."""
    store = propsys.SHGetPropertyStoreFromParsingName(
        str(path), None, GPS_DEFAULT, propsys.IID_IPropertyStore
    )
    pv = store.GetValue(PK_SYNCFLAGS)
    return pv.GetValue() if pv else 0

def is_flagged(path: Path) -> bool:
    """True if the file has exactly the '3' stuck flag."""
    return get_sync_flags(path) == TARGET_FLAG_VALUE

# ── file safety helpers ────────────────────────────────────────────────────────
def sha256(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()

def verified_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if src.stat().st_size != dst.stat().st_size or sha256(src) != sha256(dst):
        dst.unlink(missing_ok=True)
        raise IOError("checksum mismatch")

def jog_file(src: Path, temp_root: Path) -> None:
    rel_path = src.relative_to(sync_root)
    shadow   = temp_root / rel_path

    log.info(f"↻  Processing {rel_path}")

    # 1. copy → verify
    verified_copy(src, shadow)

    # 2. delete original
    src.unlink()

    # 3. copy back → verify
    verified_copy(shadow, src)

    # 4. delete shadow
    shadow.unlink()
    log.info(f"✓  Fixed      {rel_path}")

# ── main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sync_root = Path(sys.argv[1] if len(sys.argv) > 1
                     else Path.home() / "iCloudDrive").resolve()

    if not sync_root.exists():
        log.error(f"iCloud Drive folder not found: {sync_root}")
        sys.exit(1)

    temp_root = sync_root / "_iCloudFixTemp"

    # find all flagged files
    stuck_files: List[Path] = [
        p for p in sync_root.rglob("*") if p.is_file() and is_flagged(p)
    ]

    if not stuck_files:
        log.info("No files with SyncTransferStatusFlags=3 detected. ✨")
        sys.exit(0)

    log.info(f"Found {len(stuck_files)} stuck file(s)")
    log.info("-" * 60)

    try:
        for file_path in stuck_files:
            try:
                jog_file(file_path, temp_root)
            except Exception as e:
                log.error(f"!  ERROR {file_path}: {e}")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    log.info("-" * 60)
    log.info("Finished. iCloud should restart uploads for those files.")
