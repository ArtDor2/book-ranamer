import magic
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import threading

processed_files_counter = 0
counter_lock = threading.Lock()

def add_extension(file_path):
    file_type = magic.from_file(file_path, mime=True)
    mime_to_ext = {
        'application/pdf': '.pdf',
        'application/epub+zip': '.epub',
        'image/vnd.djvu': '.djvu',
        'application/zip': '.zip',
        'application/x-rar-compressed': '.rar',
        'application/rtf': '.rtf',
        'application/x-fictionbook+xml': '.fb2',
        'application/x-zip-compressed-fb2': '.fb2.zip',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/msword': '.doc',
        'application/x-chess-pgn': '.pgn',
        'text/plain': '.txt',
        'application/x-mobipocket-ebook': '.mobi'
    }
    extension = mime_to_ext.get(file_type)
    if extension:
        new_file_path = file_path + extension
        return file_type, new_file_path
    else:
        return "Unsupported file type", None

def process_file(file_path, files_to_rename):
    global processed_files_counter
    print(f"Processing file: {os.path.basename(file_path)}")
    file_type, new_file_path = add_extension(file_path)
    if new_file_path:
        files_to_rename.append((file_path, new_file_path))

    with counter_lock:
        processed_files_counter += 1
        print(f"Processed files: {processed_files_counter}")

def process_directory(directory_path, files_to_rename):
    with ThreadPoolExecutor() as executor:
        futures = []
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            if os.path.isfile(file_path):
                futures.append(executor.submit(process_file, file_path, files_to_rename))

            elif os.path.isdir(file_path):
                process_directory(file_path, files_to_rename)

        for future in futures:
            future.result()

    return files_to_rename
    

def display_files_to_rename(files_to_rename):
    print("\nFiles to be renamed:")
    for old_file_path, new_file_path in files_to_rename:
        print(f"{os.path.basename(old_file_path)} -> {os.path.basename(new_file_path)}")

def rename_files(files_to_rename):
    for old_file_path, new_file_path in files_to_rename:
        shutil.move(old_file_path, new_file_path)
        print(f"File renamed: {new_file_path}")

# Get the directory path from the user
directory_path = input("Enter the directory path: ")
files_to_rename = []

# Process the directory and get the list of files to rename
files_to_rename = process_directory(directory_path, files_to_rename)

# Display the list of files to rename
display_files_to_rename(files_to_rename)

# Ask for confirmation and rename files if confirmed
user_input = input("\nRename all files? (y/n): ").lower()
if user_input == 'y':
    rename_files(files_to_rename)
elif user_input == 'n':
    print("Files not renamed.")
else:
    print("Invalid input. Please enter 'y' or 'n'.")
