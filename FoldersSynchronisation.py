import os
import shutil
import time
import argparse
import hashlib


def calculate_md5(file_path):
    """Calculate the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def sync_folders(source_folder, replica_folder, log_file, sync_interval):
    while True:
        # First check the replica folder to identify items that need to be deleted
        for root, dirs, files in os.walk(replica_folder):
            rel_path = os.path.relpath(root, replica_folder)
            source_root = os.path.join(source_folder, rel_path)
            for file in files:
                if file in ['.DS_Store', '.directory', 'desktop.ini']:
                    continue  # .DS_Store,.directory and desktop.ini are respectively MacOS, Linux and Windows hidden
                    # files, we skip them in order they don't appear in the logs
                else:
                    replica_path = os.path.join(root, file)
                    source_path = os.path.join(source_root, file)

                    # Delete files in replica folder that are not present in source folder
                    if not os.path.exists(source_path) or calculate_md5(source_path) != calculate_md5(replica_path):
                        os.remove(replica_path)
                        with open(log_file, 'a') as log:
                            log.write(f"{time.ctime()}: Deleted {file} from {root}\n")
                        print(f"{time.ctime()}: Deleted {file} from {root}")

            for dir in dirs:
                replica_subfolder_path = os.path.join(root, dir)
                source_subfolder_path = os.path.join(source_root, dir)

                # Delete subfolders in replica that are not present in source and log changes
                if not os.path.exists(source_subfolder_path):
                    shutil.rmtree(replica_subfolder_path)
                    with open(log_file, 'a') as log:
                        log.write(f"{time.ctime()}: Deleted subfolder {dir} from {root}\n")
                    print(f"{time.ctime()}: Deleted subfolder {dir} from {root}")

        # Second, walk through the source folder to synchronize new and modified files
        for root, dirs, files in os.walk(source_folder):
            rel_path = os.path.relpath(root, source_folder)
            replica_root = os.path.join(replica_folder, rel_path)

            for file in files:
                if file in ['.DS_Store', '.directory', 'desktop.ini']:
                    continue  # .DS_Store,.directory and desktop.ini are respectively MacOS, Linux and Windows hidden
                    # files, we skip them in order they don't appear in the logs
                else:
                    source_path = os.path.join(root, file)
                    replica_path = os.path.join(replica_root, file)
                    # Copy files and log changes
                    if not os.path.exists(replica_path) or calculate_md5(source_path) != calculate_md5(replica_path):
                        shutil.copy2(source_path, replica_path)
                        with open(log_file, 'a') as log:
                            log.write(f"{time.ctime()}: Copied {file} into {replica_root}\n")
                        print(f"{time.ctime()}: Copied {file} into {replica_root}")

            for dir in dirs:
                replica_subfolder_path = os.path.join(replica_root, dir)
                source_subfolder_path = os.path.join(root, dir)
                # Copy subfolders in replica and log changes
                if not os.path.exists(replica_subfolder_path):
                    shutil.copytree(source_subfolder_path, replica_subfolder_path)
                    with open(log_file, 'a') as log:
                        log.write(f"{time.ctime()}: Copied subfolder {dir} into {replica_root}\n")
                    print(f"{time.ctime()}: Copied subfolder {dir} into {replica_root}")

        time.sleep(sync_interval)  # Wait for some fixed seconds before checking again


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Folders Synchronization")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("sync_interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    source_folder = args.source_folder
    replica_folder = args.replica_folder
    sync_interval = args.sync_interval
    log_file = args.log_file

    sync_folders(source_folder, replica_folder, log_file, sync_interval)
