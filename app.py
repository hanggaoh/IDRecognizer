import os
import shutil
from findVideo import find_all_videos
from classify import fix_name, new_Name

source_folders = ["E:\\迅雷下载"]
source_Folder_Only_Copy = ["G:\\Videos"]
destination = "E:\\AV"

def move_Or_Copy(source, dist, MOVE = True):
    videos = []
    for item in source:
        videos += find_all_videos(item)
    for vid in videos:
        new_ = new_Name(vid, dist)
        print(vid, new_)
        new_path = os.path.join(dist, new_)
        if os.path.isfile(new_path):
            continue
        if MOVE:
            shutil.move(vid, new_path)
        else:
            shutil.copy(vid, new_path)
    
if __name__ == "__main__":
    # move_Or_Copy(source_folders, destination, MOVE = True)
    # move_Or_Copy(["C:\\迅雷下载"], "H:\\AV", MOVE=True)
    # move_Or_Copy(["D:\\迅雷下载"], "D:\\AV", MOVE=True)
    # move_Or_Copy(["G:\\迅雷下载"], "G:\\Videos", MOVE=True)
    # move_Or_Copy(["G:\\"], "E:\\Videos\\AV", MOVE=False)
    # shutil.copytree("E:\\Videos\\TVs", "G:\\Videos\\TVs")
    # shutil.copytree("E:\\Videos\\Movies", "G:\\Videos\\Movies")
    # shutil.copytree("E:\\Music", "G:\\Musics")
    move_Or_Copy(source_folders, destination)

