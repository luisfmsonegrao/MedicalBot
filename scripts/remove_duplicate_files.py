import os
import hashlib
import shutil
import sys

def get_file_hash(filepath):
    """Return SHA256 hash of a file's contents."""
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def copy_unique_markdown_files(src_folder, dest_folder):
    """Copy markdown files to new folder without duplicates"""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    seen_hashes = set()
    copied_count = 0

    for filename in os.listdir(src_folder):
        if filename.lower().endswith(".md"):
            src_path = os.path.join(src_folder, filename)
            file_hash = get_file_hash(src_path)

            if file_hash not in seen_hashes:
                seen_hashes.add(file_hash)
                dest_path = os.path.join(dest_folder, filename)
                
                # If file name already exists in destination, rename it slightly
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while True:
                        new_name = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(dest_folder, new_name)
                        if not os.path.exists(dest_path):
                            break
                        counter += 1

                shutil.copy2(src_path, dest_path)
                copied_count += 1

    print(f"Copied {copied_count} unique markdown files to '{dest_folder}'.")

if __name__ == '__main__':
    curr_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    source_folder = os.path.abspath(os.path.join(curr_dir,"../data/markdowns/"))
    destination_folder = os.path.abspath(os.path.join(curr_dir,"../data/unique_markdowns/"))
    copy_unique_markdown_files(source_folder, destination_folder)