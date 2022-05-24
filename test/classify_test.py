# %%
import os
import shutil
import classify
from findVideo import find_video_files
# %%
dist_dir = "G:\\videos"
for name in find_video_files(dist_dir):
    # newname = classify.new_Name(name,dist_dir)
    print(name)
    fixed_Name = classify.fix_name(name)
    if classify.tooLong(fixed_Name):
        print(f"Moving {name}")
        shutil.move(os.path.join(dist_dir, name), os.path.join(dist_dir, "white", name))
    elif classify.find_Uncon(fixed_Name):
        print("uncon", name)
    elif classify.find_Con(fixed_Name):
        print("con", fixed_Name)
    else:
        print(f"moving {name}")
        shutil.move(os.path.join(dist_dir, name), os.path.join(dist_dir, "white", name))

