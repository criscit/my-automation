from pathlib import Path
import re
import argparse


def clean_filename(filename: str) -> str:
    new_name = re.sub(r"DataExpert\.io Boot Camp", "", filename, flags=re.IGNORECASE)

    week_match = re.search(r"Week \d+", new_name, re.IGNORECASE)
    week_str = week_match.group(0) if week_match else ""

    new_name = re.sub(r"Week \d+", "", new_name, flags=re.IGNORECASE)
    new_name = f"{week_str} {new_name}" if week_str else new_name
    new_name = re.sub(r"\s+", " ", new_name).strip()

    return new_name


def rename_files(directory: Path) -> None:
    dir_path = Path(directory)

    for file_path in dir_path.iterdir():
        if file_path.is_file():
            new_name = clean_filename(file_path.name)

            if new_name != file_path.name:
                new_path = file_path.with_name(new_name)
                file_path.rename(new_path)
                print(f"Renamed: '{file_path.name}' -> '{new_name}'")


def main():
    parser = argparse.ArgumentParser(
        description="Rename files by removing 'DataExpert.io Boot Camp', moving 'Week X' to start, and fixing spaces."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory containing files to rename (default: current directory)",
    )
    args = parser.parse_args()

    target_dir = Path(args.directory).resolve()
    if not target_dir.is_dir():
        print(f"Error: '{target_dir}' is not a valid directory")
        return

    print(f"Processing files in: {target_dir}")
    rename_files(target_dir)

if __name__ == "__main__":
    main()
