import re
import os

dir_path = r"D:/N/"
os.chdir(dir_path)
for folder_name in os.listdir(dir_path):
    if not os.path.isdir(os.path.join(dir_path, folder_name)):
        continue
    if not re.search("　\(.*?\)", folder_name):
        new_name = re.sub("　", "　()", folder_name, 1)
        os.rename(folder_name, new_name)
