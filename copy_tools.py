import os
import shutil
import typing as T
from timer import timer
import concurrent.futures


def get_file_tree(root_loc: T.Union[str, os.PathLike]) -> tuple[dict, int]:
    """
    Generate a dictionary representing the file tree of the given root location.

    Args:
        root_loc (T.Union[str, os.PathLike]): The root directory to scan.

    Returns:
        dict: A dictionary with two keys, "folders" and "files", each containing
              relative paths as keys and absolute paths as values.
    """
    total_size = 0
    tree_lookup = {"folders": {}, "files": {}}
    for root, dirs, files in os.walk(root_loc):
        for folder in dirs:
            rel = os.path.relpath(os.path.join(root, folder), root_loc)
            tree_lookup["folders"][rel] = os.path.join(root, folder)
        for file in files:
            rel = os.path.relpath(os.path.join(root, file), root_loc)
            tree_lookup["files"][rel] = os.path.join(root, file)
            total_size += os.path.getsize(os.path.join(root, file))
    return tree_lookup, int(round(total_size))


def copy_a_file(input_file: T.Union[str, os.PathLike], targ_item: T.Union[str, os.PathLike]):
    """
    Copy a file to the specified target location if the target does not already exist.

    Args:
        input_file (T.Union[str, os.PathLike]): The file to be copied.
        targ_item (T.Union[str, os.PathLike]): The target location where the file should be copied.

    Returns:
        T.Union[str, os.PathLike]: The path to the copied file if successful.
    """
    if os.path.isdir(targ_item):
        targ_item = os.path.join(targ_item, os.path.basename(input_file))
    if not os.path.exists(targ_item):
        shutil.copy2(input_file, targ_item)
    elif os.path.getmtime(input_file) > os.path.getmtime(targ_item):
        try:
            shutil.copy2(input_file, targ_item)
        except Exception as e:
            print(f"Failed to copy {targ_item}\n {e}")
            return None
    return targ_item


def list_folders_matching(input_folder: T.Union[str, os.PathLike],
                          wildcard: str) -> list[T.Union[os.PathLike, str]]:
    """
    List folders within the input folder that match the given wildcard.

    Args:
        input_folder (T.Union[str, os.PathLike]): The root directory to scan.
        wildcard (str): The wildcard string to match folder names against.

    Returns:
        list[T.Union[os.PathLike, str]]: A list of paths to matching folders.
    """
    folders = []
    for root, dirs, _ in os.walk(input_folder):
        for d in dirs:
            if wildcard.lower() in d.lower():
                folders.append(os.path.join(root, d))
    return folders


class CopyOneToMany:
    """
    A class to copy a single file to multiple folders matching a wildcard.

    Attributes:
        input_file_or_folder (T.Union[str, os.PathLike]): The file or folder to be copied.
        output_root_folder (T.Union[str, os.PathLike]): The root folder containing target folders.
        folder_wildcard (T.Union[None, str]): The wildcard to match target folders.
        output_folders (list): List of folders matching the wildcard.
    """

    def __init__(self, input_file_or_folder: T.Union[str, os.PathLike],
                 output_root_folder: T.Union[str, os.PathLike],
                 wildcard: T.Union[None, str] = None):
        """
        Initialize the CopyOneToMany class.

        Args:
            input_file_or_folder (T.Union[str, os.PathLike]): The file or folder to be copied.
            output_root_folder (T.Union[str, os.PathLike]): The root folder containing target folders.
            wildcard (T.Union[None, str], optional): The wildcard to match target folders. Defaults to None.
        """
        self.input_file_or_folder = input_file_or_folder
        self.output_root_folder = output_root_folder
        self.folder_wildcard = wildcard

        self.output_folders = []
        if self.folder_wildcard:
            self.output_folders = list_folders_matching(self.output_root_folder, self.folder_wildcard)

    def return_output_folders(self):
        """
        Return the list of output folders matching the wildcard.

        Returns:
            list: List of folders matching the wildcard.
        """
        return self.output_folders


class CopyTemplateToMultiple:
    """
    A class to copy a directory tree to multiple locations.

    Attributes:
        input_root (T.Union[str, os.PathLike]): The root directory to be copied.
        output_root_folder (T.Union[str, os.PathLike]): The root folder containing target locations.
        input_tree (dict): Dictionary representing the file tree of the input root.
    """

    def __init__(self, input_root: T.Union[str, os.PathLike],
                 output_root_folder: T.Union[str, os.PathLike]):
        """
        Initialize the CopyTemplateToMultiple class.

        Args:
            input_root (T.Union[str, os.PathLike]): The root directory to be copied.
            output_root_folder (T.Union[str, os.PathLike]): The root folder containing target locations.
        """
        self.input_root = input_root
        self.output_root_folder = output_root_folder

        self.input_tree, self.file_size = get_file_tree(self.input_root)
        self.file_size = int(round(self.file_size * 1e-6))

    def copy_the_tree(self) -> dict:
        """
        Copy the directory tree to the target location.

        Returns:
            dict: A dictionary with two keys, "folders" and "files", each containing
                  lists of created folders and files.
        """
        things_created = {"folders": [], "files": []}

        # Create root if DNE
        if not os.path.exists(self.output_root_folder):
            os.makedirs(self.output_root_folder)
            things_created["folders"].append(self.output_root_folder)

        # Create subfolders in target location
        for rel_folder, inpath in self.input_tree["folders"].items():
            targ_item = os.path.join(self.output_root_folder, rel_folder)
            if not os.path.exists(targ_item):
                os.makedirs(targ_item, exist_ok=True)
                things_created["folders"].append(targ_item)

        # Create files in target location
        # Decide to use threads or not
        if self.file_size > 250 and len(self.input_tree["files"]) > 10:
            futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for rel_file, inpath in self.input_tree["files"].items():
                    targ_item = os.path.join(self.output_root_folder, rel_file)
                    futures.append(executor.submit(copy_a_file, inpath, targ_item))
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    things_created["files"].append(future.result())
        # Copy files in main thread
        for rel_file, inpath in self.input_tree["files"].items():
            targ_item = os.path.join(self.output_root_folder, rel_file)
            things_created["files"].append(copy_a_file(inpath, targ_item))

        return things_created


def copy_one_to_many(input_file: T.Union[str, os.PathLike],
                     output_root_folder: T.Union[str, os.PathLike],
                     wildcard: T.Union[None, str] = None):
    """
    Copy a single file to multiple folders matching a wildcard.

    Args:
        input_file (T.Union[str, os.PathLike]): The file to be copied.
        output_root_folder (T.Union[str, os.PathLike]): The root folder containing target folders.
        wildcard (T.Union[None, str], optional): The wildcard to match target folders. Defaults to None.
    """
    # Call the class to copy one to many
    result = CopyOneToMany(input_file, output_root_folder, wildcard)
    output_folders = result.return_output_folders()

    # Perform copy on each folder found previously
    print(f"Copying to {len(output_folders)} folders...")
    copied = []
    if output_folders:
        for folder in output_folders:
            copy_a_file(input_file, folder)
            copied.append(folder)

    # Print results
    for i in range(0, len(copied), 2):
        print(f'Copied:')
        print(f"   {copied[:i]}")


def copy_template_to_multiple(input_root: T.Union[str, os.PathLike],
                              output_root_folder: T.Union[str, os.PathLike]):
    """
    Copy a directory tree to multiple locations.

    Args:
        input_root (T.Union[str, os.PathLike]): The root directory to be copied.
        output_root_folder (T.Union[str, os.PathLike]): The root folder containing target locations.
    """
    # Call class to copy a source tree to target folder
    result = CopyTemplateToMultiple(input_root, output_root_folder)
    things_created = result.copy_the_tree()
    print(f"Finished copying template to {output_root_folder}")

    # Print the results returned as dictionary
    for ftype, items in things_created.items():
        print(f"{ftype.capitalize()}:")
        for item in items:
            print(f"   {item}")


if __name__ == "__main__":
    inroot = "/Users/kevin/Library/CloudStorage/OneDrive-kevingabelman/pinal/RFIRM_2023_1204"
    outroot = "/Users/kevin/test"

    # Call function method
    timer(copy_template_to_multiple)(inroot, outroot)
