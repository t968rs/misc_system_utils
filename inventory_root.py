import os
import logging
import json
import typing as T


def inventory_root_path(path: T.Union[str, os.PathLike]) -> (
        T.Tuple)[T.Dict[str, os.PathLike], T.Dict[str, os.PathLike]]:
    # Inventory the root path
    folder_lookup: T.Dict[str, os.PathLike] = {}
    file_lookup: T.Dict[str, os.PathLike] = {}
    for root, dirs, files in os.walk(path):
        for folder in dirs:
            rel = os.path.relpath(os.path.join(root, folder), path)
            folder_lookup[rel] = os.path.join(root, folder)
        for file in files:
            rel = os.path.relpath(os.path.join(root, file), path)
            file_lookup[rel] = os.path.join(root, file)
    return folder_lookup, file_lookup


def log_inventory(root_path):
    folders, files = inventory_root_path(root_path)
    logger.info(f"Inventory of {root_path}")
    for folder, path in folders.items():
        logger.info(f"Folder: {folder}")

    unique_files = []
    for file, path in files.items():
        unique_files.append(file)
    unique_files = list(set(unique_files))
    logger.info(f"Unique files: {len(unique_files)}")

    with open(f"{root_path}/inventory.json", "w") as f:
        json_dict = {"Unique Files": unique_files, "Folders": folders}
        json.dump(json_dict, f)


path_to_inventory = r"C:\Users\t968rs\Pictures"
base, folder_name = os.path.split(path_to_inventory)
log_path = os.path.join(base, f"{folder_name}_inventory.log")
logger = logging.getLogger("inventory_root")
logging.basicConfig(level=logging.INFO, filename=log_path, filemode="a",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_inventory(r"C:\Users\t968rs\Pictures")
