import os
import shutil
import time


def get_file_tree(root_loc):
    tree_lookup = {"folders": {}, "files": {}}
    walker = os.walk(root_loc)
    for root, dirs, files in walker:
        for folder in dirs:
            rel = os.path.relpath(os.path.join(root, folder), root_loc)
            tree_lookup["folders"][rel] = os.path.join(root, folder)
        for file in files:
            rel = os.path.relpath(os.path.join(root, file), root_loc)
            tree_lookup["files"][rel] = os.path.join(root, file)
    return tree_lookup

def copy_file(input_file, output_folder):
    filename = os.path.split(input_file)[1]
    outpath = os.path.join(output_folder, filename)
    shutil.copy2(input_file, outpath)
    if os.path.exists(outpath):
        print(f"Copied {filename}\n   to {outpath}")
        return outpath
    else:
        print(f"Failed to copy {filename}")
        return None

def list_folders_matching(input_folder, wildcard):
    folders = []
    walker = os.walk(input_folder)
    for root, dirs, files in walker:
        for d in dirs:
            if wildcard.lower() in d.lower():
                folders.append(os.path.join(root, d))
    return folders

class CopyOneToMany:
    def __init__(self, input_file_or_folder, output_root_folder, wildcard=None):
        self.input_file_or_folder = input_file_or_folder
        self.output_root_folder = output_root_folder
        self.folder_wildcard = wildcard

        self.output_folders = []
        if self.folder_wildcard:
            self.output_folders = list_folders_matching(self.output_root_folder, self.folder_wildcard)


    def return_output_folders(self):
        return self.output_folders

def copy_one_to_many(input_file, output_root_folder, wildcard=None):
    result = CopyOneToMany(input_file, output_root_folder, wildcard)
    output_folders = result.return_output_folders()

    print(f"Copying to {len(output_folders)} folders...")
    copied = []
    if output_folders:
        for folder in output_folders:
            copy_file(input_file, folder)
            copied.append(folder)
    for i in range(0, len(copied), 2):
        print(f'Copied:')
        print(f"   {copied[:i]}")



class CopyTemplateToMultiple:
    def __init__(self, input_root, output_root_folder):
        self.input_root = input_root
        self.output_root_folder = output_root_folder

        self.input_tree = get_file_tree(self.input_root)

    def check_output_root(self):
        things_created = {"folders": [], "files": []}

        if not os.path.exists(self.output_root_folder):
            os.makedirs(self.output_root_folder)
            things_created["folders"].append(self.output_root_folder)

        for rel_folder, inpath in self.input_tree["folders"].items():
            targ_item = os.path.join(self.output_root_folder, rel_folder)
            if not os.path.exists(targ_item):
                os.makedirs(targ_item, exist_ok=True)
                things_created["folders"].append(targ_item)
            else:
                print(f"Folder {targ_item} already exists")

        for rel_file, inpath in self.input_tree["files"].items():
            targ_item = os.path.join(self.output_root_folder, rel_file)
            if not os.path.exists(targ_item):
                shutil.copy2(inpath, targ_item)
                things_created["files"].append(targ_item)
                print(f"Copied {targ_item}")
            elif os.path.getmtime(inpath) > os.path.getmtime(targ_item):
                try:
                    shutil.copy2(inpath, targ_item)
                    things_created["files"].append(targ_item)
                    print(f"Updated {targ_item}")
                except Exception as e:
                    print(f"Failed to copy {targ_item}\n {e}")

            else:
                print(f"File {targ_item} already exists")

        return things_created

def copy_template_to_multiple(input_root, output_root_folder):
    result = CopyTemplateToMultiple(input_root, output_root_folder)
    things_created = result.check_output_root()
    print(f"Finished copying template to {output_root_folder}")
    for ftype, items in things_created.items():
        print(f"{ftype.capitalize()}:")
        for item in items:
            print(f"   {item}")

if __name__ == "__main__":
    inroot = r"E:\guidance\lessons"
    outroot = r"E:\test"
    copy_template_to_multiple(inroot, outroot)
