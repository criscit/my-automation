from pathlib import Path
from datetime import datetime

# Folder containing individual .md test files
input_folder = Path(r"C:\Users\crisc\iCloudDrive\iCloud~md~obsidian\personal-info\Health\Medical Record\Tests")

# Name for the compilation theme (same as the input folder’s name)
combination_theme = input_folder.name

# Output folder next to the Tests directory
output_folder = input_folder.parent / "Combinations"
output_folder.mkdir(parents=True, exist_ok=True)

# Timestamp for unique file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
output_file = output_folder / f"{combination_theme}_{timestamp}.md"

# Collect all .md files, sorted alphabetically for consistency
md_files = sorted(input_folder.glob("*.md"))

with output_file.open("w", encoding="utf-8") as outfile:
    for idx, md_file in enumerate(md_files, start=1):
        # Write the filename (without extension) as an H1 header
        outfile.write(f"# {md_file.stem}\n\n")

        # Append the file’s content
        outfile.write(md_file.read_text(encoding="utf-8").rstrip())
        outfile.write("\n")  # ensure final newline inside section

        # Add a separator line after each file except the last
        if idx < len(md_files):
            outfile.write("\n***\n\n")

print(f"Combined file created at: {output_file}")
