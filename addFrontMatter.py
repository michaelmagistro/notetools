#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def add_frontmatter_to_file(file_path, category, title):
    """
    Add YAML frontmatter to the top of a file.
    
    Args:
        file_path (Path): Path to the file
        category (str): Category for the frontmatter
        title (str): Title for the frontmatter
    """
    # Read the existing content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    # Check if frontmatter already exists
    if content.startswith('---'):
        print(f"Skipping {file_path.name} - frontmatter already exists")
        return False

    # Create the frontmatter
    frontmatter = f"""---
layout: general
title: {title}
categories: [{category}]
tags: []
author: Michael Magistro
---

"""

    # Combine frontmatter with existing content
    new_content = frontmatter + content

    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Added frontmatter to {file_path.name}")
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False


def extract_title_from_filename(filename):
    """
    Use the complete filename as the title, including extension.
    
    Args:
        filename (str): The filename
        
    Returns:
        str: The complete filename as title
    """
    return filename


def process_folder(folder_path, category):
    """
    Process all .txt files in the given folder.
    
    Args:
        folder_path (str): Path to the folder containing .txt files
        category (str): Category to add to frontmatter
    """
    folder = Path(folder_path)

    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist")
        return

    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory")
        return

    # Find all .txt files
    txt_files = list(folder.glob('*.txt'))

    if not txt_files:
        print(f"No .txt files found in '{folder_path}'")
        return

    print(f"Found {len(txt_files)} .txt files in '{folder_path}'")
    print(f"Using category: '{category}'")
    print("-" * 50)

    processed_count = 0
    skipped_count = 0

    for txt_file in txt_files:
        title = extract_title_from_filename(txt_file.name)

        if add_frontmatter_to_file(txt_file, category, title):
            processed_count += 1
        else:
            skipped_count += 1

    print("-" * 50)
    print(f"Processing complete:")
    print(f"  Files processed: {processed_count}")
    print(f"  Files skipped: {skipped_count}")


def main():
    """Main function to run the script with hardcoded path and category."""
    # SET YOUR FOLDER PATH AND CATEGORY HERE
    folder_path = "~/Dropbox/notes_personal"  # Change this to your actual folder path
    category = "personal"            # Change this to your desired category

    # Expand the ~ to the full home directory path
    folder_path = os.path.expanduser(folder_path)

    print(f"Adding frontmatter to .txt files...")
    print(f"Folder: {folder_path}")
    print(f"Category: {category}")
    process_folder(folder_path, category)


if __name__ == "__main__":
    main()
