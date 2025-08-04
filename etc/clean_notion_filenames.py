import re
from pathlib import Path
from urllib.parse import quote
import argparse
import unicodedata

def clean_filename(name):
    # Remove Notion hash (32+ hex at end, optional space/_)
    cleaned = re.sub(r'[\s_]*[a-f0-9]{32,}$', '', name)
    cleaned = re.sub(r'[\s_]+', ' ', cleaned)
    cleaned = cleaned.strip()
    cleaned = unicodedata.normalize("NFC", cleaned)
    return cleaned

def build_old_to_new(folder):
    """
    Map every hashed filename/foldername (url-encoded) to cleaned name (url-encoded)
    Only by basename, not full path!
    """
    mapping = {}
    for item in folder.rglob("*"):
        old = item.name
        if item.is_file():
            stem = clean_filename(item.stem)
            suffix = item.suffix
            new = stem + suffix
        else:
            new = clean_filename(item.name)
        if old != new:
            # Add both NFC and NFD old names, both raw and encoded
            old_norm_nfc = unicodedata.normalize('NFC', old)
            mapping[quote(old_norm_nfc)] = quote(new)
            old_norm_nfd = unicodedata.normalize('NFD', old)
            mapping[quote(old_norm_nfd)] = quote(new)
    return mapping

def rename_files_and_folders(folder):
    # Files first (deepest), then folders
    for item in sorted(folder.rglob("*"), key=lambda x: -len(str(x))):
        if item.is_file():
            new_name = clean_filename(item.stem) + item.suffix
            if new_name != item.name:
                item.rename(item.with_name(new_name))
    for item in sorted([p for p in folder.rglob("*") if p.is_dir()], key=lambda x: -len(str(x))):
        new_name = clean_filename(item.name)
        if new_name != item.name:
            item.rename(item.with_name(new_name))

def replace_links_in_md_files(folder, mapping):
    for md_file in folder.rglob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()
        new_text = text
        for old, new in mapping.items():
            # Both old and new are already normalized and quoted
            new_text = new_text.replace(old, new)
        if new_text != text:
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(new_text)
            print(f"Updated: {md_file}")

def main():
    parser = argparse.ArgumentParser(description="Clean Notion clutter and fix internal links.")
    parser.add_argument("folder", help="Path to the folder containing Notion export files and folders")
    args = parser.parse_args()
    folder = Path(args.folder)
    mapping = build_old_to_new(folder)
    rename_files_and_folders(folder)
    replace_links_in_md_files(folder, mapping)


if __name__ == "__main2__":
    main()

if __name__ == "__main__":
    folder = Path(r"C:\Users\crisc\Downloads\Test\notion-final-normal-export")
    mapping = build_old_to_new(folder)
    rename_files_and_folders(folder)
    replace_links_in_md_files(folder, mapping)
