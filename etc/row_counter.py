from collections import Counter


def count_rows(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.rstrip('\n') for line in file]

    counts = Counter(lines)

    for line, count in counts.items():
        if count != 2:
            print(f"{repr(line)}: {count}")


# Example usage:
file_path = r"C:\Users\crisc\iCloudDrive\iCloud~md~obsidian\personal-info\Content to Consume\Content to Clean.md"  # Replace with your actual file path
count_rows(file_path)
