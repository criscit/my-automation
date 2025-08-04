#!/usr/bin/env python
"""
find_stuck_downloads.py  –  List iCloud files flagged as
STS_NEEDSDOWNLOAD (0x2) while NOT transferring (0x4).

Requires:
    pip install pywin32
Usage:
    python find_stuck_downloads.py             # auto-detect iCloudDrive
    python find_stuck_downloads.py "D:\\iCloud"  # explicit path
"""

from __future__ import annotations
import sys, csv
from pathlib import Path
import pythoncom
from win32com.propsys import propsys, pscon

GPS_DEFAULT = getattr(pscon, "GPS_DEFAULT", 0)
PK_SYNCFLAGS = propsys.PSGetPropertyKeyFromName("System.SyncTransferStatusFlags")

NEED_DOWNLOAD = 0x2
TRANSFERRING  = 0x4

def get_flags(path: Path) -> int:
    """Return SyncTransferStatusFlags as an *int* (0 if missing/None)."""
    store = propsys.SHGetPropertyStoreFromParsingName(
        str(path), None, GPS_DEFAULT, propsys.IID_IPropertyStore
    )
    pv = store.GetValue(PK_SYNCFLAGS)
    val = pv.GetValue() if pv else 0
    return int(val or 0)

def is_stuck_dl(path: Path) -> bool:
    flags = get_flags(path)
    return (flags & NEED_DOWNLOAD) and not (flags & TRANSFERRING)

if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "iCloudDrive")
    if not root.exists():
        sys.exit(f"iCloud Drive not found at {root}")

    stuck = [p for p in root.rglob("*") if p.is_file() and is_stuck_dl(p)]

    if not stuck:
        print("✅ No files are stuck in downloading.")
        sys.exit(0)

    print(f"⚠️  {len(stuck)} file(s) are waiting to download but not moving:\n")
    for p in stuck:
        print(p)

    # optional: dump to CSV for easier inspection
    with open("stuck_downloads.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["Path", "Flags"])
        for p in stuck:
            wr.writerow([str(p), get_flags(p)])
    print("\nList also saved to stuck_downloads.csv")
