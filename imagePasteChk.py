#!/usr/bin/env python3
"""
Script to find broken image links in text files across multiple folders.
Searches for ![](imagepaste/filename.png) patterns and checks if the image exists.
"""

import os
import re
import csv
from pathlib import Path


def find_image_references(file_path):
    """
    Find all image references in a text file that match the pattern ![](imagepaste/filename.png)
    Returns a list of image filenames found.
    """
    image_pattern = r'!\[\]\(imagepaste/([^)]+)\)'
    image_references = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            matches = re.findall(image_pattern, content)
            image_references.extend(matches)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

    return image_references


def check_image_exists(folder_path, image_name):
    """
    Check if an image exists in the imagepaste subfolder.
    Returns True if found, False otherwise.
    """
    imagepaste_path = os.path.join(folder_path, 'imagepaste', image_name)
    return os.path.isfile(imagepaste_path)


def process_folder(folder_path):
    """
    Process all .txt files in a folder and return results.
    Returns a list of tuples: (folder_name, file_name, image_name, exists)
    """
    results = []
    folder_name = os.path.basename(folder_path)

    if not os.path.exists(folder_path):
        print(f"Warning: Folder {folder_path} does not exist. Skipping.")
        return results

    print(f"Processing folder: {folder_path}")

    # Find all .txt files in the folder
    for root, dirs, files in os.walk(folder_path):
        # Skip the imagepaste folder itself
        if 'imagepaste' in root:
            continue

        for file in files:
            if file.lower().endswith('.txt'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)

                # Find image references in this file
                image_refs = find_image_references(file_path)

                for image_name in image_refs:
                    exists = check_image_exists(folder_path, image_name)
                    status = "Found" if exists else "Missing"

                    results.append(
                        (folder_name, relative_path, image_name, status))
                    print(f"  {relative_path}: {image_name} -> {status}")

    return results


def main():
    # List of folders to search
    folders_to_search = [
        os.path.expanduser("~/dropbox/notes_personal"),
        # Assuming this was meant instead of duplicate
        os.path.expanduser("~/dropbox/notes_work"),
        os.path.expanduser("~/dropbox/notes_crypto")
    ]

    all_results = []

    # Process each folder
    for folder in folders_to_search:
        folder_results = process_folder(folder)
        all_results.extend(folder_results)

    # Write results to CSV file
    output_file = "outputs/brokenimagelinks.txt"

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # Using tab delimiter for .txt file
        writer = csv.writer(csvfile, delimiter='\t')

        # Write header
        writer.writerow(['Folder', 'File', 'Image', 'Status'])

        # Write data
        for result in all_results:
            writer.writerow(result)

    print(f"\nResults written to {output_file}")
    print(f"Total image references found: {len(all_results)}")

    # Summary statistics
    missing_count = sum(1 for result in all_results if result[3] == "Missing")
    found_count = len(all_results) - missing_count

    print(f"Images found: {found_count}")
    print(f"Images missing: {missing_count}")


if __name__ == "__main__":
    main()
