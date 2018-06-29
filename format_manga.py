import re
import os

dir_path = r"D:\\N"
os.chdir(dir_path)

for folder_name in os.listdir(dir_path):
    if not os.path.isdir(os.path.join(dir_path, folder_name)):
        continue
    
    if not re.search("^(\(.*?\))? ?\[.*?\].*?$", folder_name):
        continue
		
    new_name = re.sub(" ?\[(\d{7}|DL.|別.*?)\]", "", folder_name, flags=re.IGNORECASE)
    info = re.sub("\[\d{7}\]$", "", folder_name.replace(new_name, ""))
    
    new_name = re.sub("^(\(.*?\))? ?\[(?P<author>.*?)\] ?(?P<name>.*?)$",
                        "\g<author>　()\g<name>",
                        new_name,
                        flags=re.IGNORECASE)\
		 .strip()
						
    while os.path.isdir(new_name) :
        if info != "":
            new_name += info
            info = ""
        else:
            new_name += " [another]"
    print("{: <30}".format(folder_name), "\t->", new_name)
    os.rename(folder_name, new_name)

os.system("pause")
