import re
import os

dir_path = r"C:/TEST/"
os.chdir(dir_path)
for folder_name in os.listdir(dir_path):
    if not os.path.isdir(os.path.join(dir_path, folder_name)):
        continue
    
    new_name = re.sub(" ?\[(\d{6}|DL.|別.*?)\]", "", folder_name, flags=re.IGNORECASE)
    #Prevent duplicated name when there are more than two version exist.
    info = folder_name.replace(new_name, "")
    info = re.sub("\[\d{6}\]$", "", info)
    new_name = re.sub("^(\(.*?\))? ?(\[.*?\]) ?(?P<name_front>.*?年)(?P<month>\d+)(?P<name_rear>月.*?)",
                      lambda m : m.group("name_front") + m.group("month").zfill(2) + m.group("name_rear"),
                      new_name)
    new_name = re.sub("VOL", "Vol", new_name, flags=re.IGNORECASE)
    new_name = new_name.strip()

    if os.path.isdir(new_name) :
        new_name += info
    os.rename(folder_name, new_name)
    
os.system(r"del /s g*.txt")
