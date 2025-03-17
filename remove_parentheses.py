import re
import os

dir_path = r"D:/N/"
os.chdir(dir_path)

for folder_name in os.listdir(dir_path):
    if not os.path.isdir(os.path.join(dir_path, folder_name)):
        continue
    
    new_name = re.sub(r"　\(\)", "　", folder_name, 1)
    if new_name != folder_name:
        print(folder_name.ljust(40), "->", new_name)
        os.rename(folder_name, new_name)

os.system("pause")
