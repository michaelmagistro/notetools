#!/usr/bin/env python3
"""
Script to find broken image links in text files across multiple folders.
Searches for ![title](imagepaste/filename.png) patterns and checks if the image exists.
Also performs reverse check to find orphaned images.
"""

import os
import re
import csv
from pathlib import Path


def find_image_references(file_path):
    """
    Find all image references in a text file that match the pattern ![title](imagepaste/filename.png)
    Returns a list of image filenames found.
    """
    # Updated regex to handle optional titles: ![optional title](imagepaste/filename.png)
    image_pattern = r'!\[([^\]]*)\]\(imagepaste/([^)]+)\)'
    image_references = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            matches = re.findall(image_pattern, content)
            # Extract just the filename (second group in the match)
            image_references = [match[1] for match in matches]
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


def find_all_images_with_status(folders_to_search, referenced_images):
    """
    Find all images in imagepaste folders and check if they are referenced in text files.
    Returns a list of tuples: (image_path, status)
    """
    all_images_status = []

    for folder in folders_to_search:
        if not os.path.exists(folder):
            continue

        folder_name = os.path.basename(folder)
        imagepaste_path = os.path.join(folder, 'imagepaste')

        if not os.path.exists(imagepaste_path):
            print(f"No imagepaste folder found in {folder}")
            continue

        print(f"\nChecking all images in: {imagepaste_path}")

        # Get all image files in imagepaste folder
        image_files = []
        try:
            for file in os.listdir(imagepaste_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')):
                    image_files.append(file)
        except Exception as e:
            print(f"Error reading imagepaste folder {imagepaste_path}: {e}")
            continue

        # Check each image file
        for file in sorted(image_files):  # Sort for consistent output
            image_path = f"{folder_name}/imagepaste/{file}"
            # Check if this image is referenced in our extracted list
            if file in referenced_images:
                status = "referenced"
                print(f"  Referenced: {file}")
            else:
                status = "orphaned"
                print(f"  Orphaned: {file}")

            all_images_status.append((image_path, status))

    return all_images_status


def main():
    # List of folders to search
    folders_to_search = [
        os.path.expanduser("~/dropbox/notes_personal"),
        os.path.expanduser("~/dropbox/notes_technical"),
        os.path.expanduser("~/dropbox/notes_crypto")
    ]

    all_results = []
    all_referenced_images = set()  # Track all images referenced in text files

    # Process each folder
    for folder in folders_to_search:
        print(f"\nAttempting to process: {folder}")
        if os.path.exists(folder):
            folder_results = process_folder(folder)
            all_results.extend(folder_results)
            # Collect all referenced image names
            for result in folder_results:
                # Image name is in column 3
                all_referenced_images.add(result[2])
        else:
            print(f"ERROR: Folder does not exist: {folder}")
            # Still add an entry to show the folder was checked
            folder_name = os.path.basename(folder)
            all_results.append(
                (folder_name, "FOLDER_NOT_FOUND", "N/A", "Folder does not exist"))

    # Find all images and their status (reverse check)
    print(f"\n{'='*50}")
    print("CHECKING ALL IMAGES IN IMAGEPASTE FOLDERS")
    print(f"{'='*50}")

    all_images_status = find_all_images_with_status(
        folders_to_search, all_referenced_images)

    # Create outputs directory if it doesn't exist
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Write results to file
    output_file = os.path.join(output_dir, "brokenimagelinks.txt")

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # Using tab delimiter for .txt file
        writer = csv.writer(csvfile, delimiter='\t')

        # Write header for main results
        writer.writerow(['Folder', 'File', 'Image', 'Status'])

        # Write main data
        for result in all_results:
            writer.writerow(result)

        # Write separator
        writer.writerow([])  # Empty line
        writer.writerow(['---'])  # Separator
        writer.writerow([])  # Empty line

        # Write all images section
        for image_info in all_images_status:
            # image_path, status
            writer.writerow([image_info[0], image_info[1]])

    print(f"\nResults written to {output_file}")
    print(f"Total image references found: {len(all_results)}")

    # Summary statistics
    missing_count = sum(1 for result in all_results if result[3] == "Missing")
    found_count = len(all_results) - missing_count
    orphaned_count = sum(
        1 for img in all_images_status if img[1] == "orphaned")
    referenced_count = len(all_images_status) - orphaned_count

    print(f"Images found: {found_count}")
    print(f"Images missing: {missing_count}")
    print(f"Total images in imagepaste folders: {len(all_images_status)}")
    print(f"Images referenced: {referenced_count}")
    print(f"Orphaned images: {orphaned_count}")


if __name__ == "__main__":
    main()
