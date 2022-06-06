import os
import shutil
from findVideo import find_all_videos
from classify import new_Name

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
    # shutil.copytree("E:\\Videos\\TVs", "G:\\Videos\\TVs")
    # shutil.copytree("E:\\Videos\\Movies", "G:\\Videos\\Movies")
    # shutil.copytree("E:\\Music", "G:\\Musics")
    move_Or_Copy(["D:\\download"], "D:\\Av")
    move_Or_Copy(["C:\\迅雷下载", "E:\\download"], "E:\\Videos\\Active")

