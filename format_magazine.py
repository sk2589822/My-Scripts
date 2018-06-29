import re
import os

dir_path = r"G:/EX-II/雑誌/"
os.chdir(dir_path)
for folder_name in os.listdir(dir_path):
    if not os.path.isdir(os.path.join(dir_path, folder_name)):
        continue
    
    new_name = re.sub(" ?\[(\d{7}|DL.|別.*?)\]", "", folder_name, flags=re.IGNORECASE)
    #Prevent duplicated name when there are more than two version exist.
    info = folder_name.replace(new_name, "")
    info = re.sub("\[\d{7}\]$", "", info)
    if re.search("年\d+月", new_name):
        new_name = re.sub("^(\(.*?\))? ?(\[.*?\]) ?(?P<name_front>.*?年)(?P<month>\d+)(?P<name_rear>月.*?)$",
			  lambda m : m.group("name_front") + m.group("month").zfill(2) + m.group("name_rear"),
			  new_name)
        
    else:
        new_name = re.sub("^(\(.*?\))? ?(\[.*?\]) ?(?P<name>.*?)$", "\g<name>", new_name)
	
    new_name = re.sub("VOL", "Vol", new_name, flags=re.IGNORECASE)
    new_name = new_name.strip()

    if os.path.isdir(new_name) :
        new_name += info
    os.rename(folder_name, new_name)
