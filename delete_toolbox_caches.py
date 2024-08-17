import os
import shutil
import time

folder_path = r'A:\automation\toolboxes\__pycache__'  # Replace with your folder path


def delete_tool_cahces():
    try:
        # Attempt to delete the folder
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' has been successfully deleted.")
    except Exception as e:
        print(f"Failed to delete folder '{folder_path}': {e}")

        # If deletion fails, delete the contents of the folder instead
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
            print(f"Contents of folder '{folder_path}' have been deleted.")
        except Exception as e:
            print(f"Failed to delete contents of folder '{folder_path}': {e}")


while True:
    sleep_time = 300
    delete_tool_cahces()
    print(f"Sleeping for {sleep_time / 60} minutes")
    time.sleep(sleep_time)
