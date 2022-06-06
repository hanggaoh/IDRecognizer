import os

EXTENTION_VIDEO = ["avi", "mp4", "wmv", "mkv", "rmvb", "m4v", "mov", "iso", "ts", "mpeg", "vob", "mpg"]

def _file_extention(path):
    return path.split('.')[-1].lower()

def _find_all_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            yield(os.path.join(root,file))


def find_video_files(path):
    lst_vids_path = []
    for name in os.listdir(path):
        if _file_extention(name) in EXTENTION_VIDEO:
            lst_vids_path.append(name)
    return(lst_vids_path)

def find_all_videos(path):
    lst_vids_path = []
    for item in _find_all_files(path):
        if _file_extention(item) in EXTENTION_VIDEO:
            lst_vids_path.append(item)
    return(lst_vids_path)
