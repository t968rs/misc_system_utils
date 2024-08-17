import os
import shutil
import time
import typing as T


def delete_folder_and_contents(folder: T.Union[str, os.PathLike]):
    """
    Delete the specified folder and its contents. If the folder cannot be deleted,
    attempt to delete its contents instead.

    Raises:
        Exception: If an error occurs during the deletion process.
    """
    try:
        # Attempt to delete the folder
        shutil.rmtree(folder)
        print(f"Folder '{folder}' has been successfully deleted.")
    except Exception as e:
        print(f"Failed to delete folder '{folder}': {e}")

        # If deletion fails, delete the contents of the folder instead
        try:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
            print(f"Contents of folder '{folder}' have been deleted.")
        except Exception as e:
            print(f"Failed to delete contents of folder '{folder}': {e}")


# Folder path to delete
folder_path = r'A:\automation\toolboxes\__pycache__'  # Replace with your folder path

while True:
    sleep_time = 300  # Time to sleep between deletions in seconds
    delete_folder_and_contents(folder_path)
    print(f"Sleeping for {sleep_time / 60} minutes")
    time.sleep(sleep_time)
    #
