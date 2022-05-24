import os
import shutil

# TODO finish the clean disk scripts
def remove_useless_files(path):
    for item in os.listdir(path):
        if item.split(".")[-1] == "torrent":
            os.remove(os.path.join(path, item))

def remove_parent_folder():
    pass

def remove_empty_folder(path):
    if os.path.getsize(path) < 150 * 1024:
        shutil.rmtree(path)

def remove_Empty_In_Folder(dist_Folder):
    for item in os.listdir(dist_Folder):
        if  os.path.isdir(os.path.join(dist_Folder, item)):
            remove_empty_folder(os.path.join(dist_Folder, item))