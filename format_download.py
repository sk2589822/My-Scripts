import re
import os
import pathlib

dir_path = r"H:\\HentaiAtHome\\download"
os.chdir(dir_path)

for folder_name in os.listdir(dir_path) :
    if not os.path.isdir(os.path.join(dir_path, folder_name)):
        continue
    
    if not re.search("[^\[\(]* \[\d{6,7}(-\d*x)?\]$", folder_name):
        continue
    
    new_name = re.sub(" ?\[(\d{6,7}(-\d*x)?|DL.|別.*?)\]", "", folder_name, flags=re.IGNORECASE)
    info = re.sub("\[\d{6,7}(-\d*x)?\]$", "", folder_name.replace(new_name, ""))

    #pattern = r"^((?P<session_1>\(.*?\d+.*?\))? ?(\[(?P<author>.*?)\])? ?(?P<name>[^\[\(]*)) ?(?P<session_2>\(.*?\d+.*?\))? ?(?P<parody>\(.*?\))?$"
    #repl = r"\g<author>---ForSplit---\g<session_1>\g<session_2>    \g<name> \g<parody>"
    pattern = r"^((?P<session>\(.*?\d+.*?\))? ?(\[(?P<author>.*?)\])? ?(?P<name>.*))$"
    repl = r"\g<author>---ForSplit---\g<session> \g<name>"
    new_name = re.sub(pattern, repl, new_name,  flags=re.IGNORECASE)\
                 .strip()

    if re.search("---ForSplit---", new_name): 
        author, new_name = new_name.split("---ForSplit---", 1)
        new_name = new_name.strip()
        if author != "":
            pathlib.Path(author).mkdir(parents=True, exist_ok=True)
            new_name = os.path.join(dir_path, author, new_name)
        while os.path.isdir(new_name) :
            if info != "":
                new_name += info
                info = ""
            else:
                new_name += " [another]"
        print(folder_name)
        print(new_name.replace(dir_path, ""))
        os.rename(folder_name, new_name)
        
os.system("pause")
