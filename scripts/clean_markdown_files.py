import os
import re
import sys

def clean_file(filepath):
    """Remove * and # characters and collapse multiple spaces (but keep newlines)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove * and # characters
    cleaned = content.replace("*", "").replace("#", "")

    # Collapse multiple spaces/tabs within lines
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    # Collapse multiple blank lines (optional)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)

    # Strip trailing spaces on each line
    cleaned = "\n".join(line.rstrip() for line in cleaned.splitlines())

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cleaned)

def clean_markdown_folder(folder_path):
    """Clean all markdown files in the given folder."""
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".md"):
            filepath = os.path.join(folder_path, filename)
            clean_file(filepath)
            print(f"✅ Cleaned: {filename}")

# Example usage:
folder = os.path.dirname(os.path.abspath(sys.argv[0]))
folder = os.path.abspath(os.path.join(folder,'../data/unique_markdowns'))
clean_markdown_folder(folder)