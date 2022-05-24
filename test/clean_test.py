import os
import clean

dist_name = "G:\\迅雷下载"

for item in os.listdir(dist_name):
    if  os.path.isdir(os.path.join(dist_name, item)):
        clean.remove_empty_folder(os.path.join(dist_name, item))