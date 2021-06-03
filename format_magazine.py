import re
import os

dir_path = r"G:\\EX-II\\雑誌"
os.chdir(dir_path)

for folder_name in os.listdir(dir_path):
    if not os.path.isdir(os.path.join(dir_path, folder_name)):
        continue

    if not re.search(r"^(\(.*?\))? ?(\[.*?\]).*?$", folder_name):
        continue

    new_name = re.sub(r" ?\[(\d{6,7}|DL.|別.*?)\]$", "", folder_name, flags=re.IGNORECASE)
    info = re.sub(r"\[\d{6,7}\]$", "", folder_name.replace(new_name, ""))

    if re.search(r"年\d+月", new_name):
        new_name = re.sub(r"^(\(.*?\))? ?(\[.*?\]) ?(?P<name_front>.*?年)(?P<month>\d+)(?P<name_rear>月.*?)$",
            lambda m : m.group("name_front") + m.group("month").zfill(2) + m.group("name_rear"),
            new_name)

    else:
        new_name = re.sub(r"^(\(.*?\))? ?(\[.*?\]) ?(?P<name>.*?)$", r"\g<name>", new_name)

    new_name = re.sub(r"VOL", "Vol", new_name, flags=re.IGNORECASE)
    new_name = re.sub(r"コミック・?|マガジン|COMIC|COMlC", "", new_name, flags=re.IGNORECASE)

    new_name = new_name \
        .replace("(ゼロス) #", "（ゼロス） ＃") \
        .replace("Girls forM (ガールズフォーム)", "ガールズフォーム") \
        .replace("(コミック エグゼ) ", "Vol.") \
        .replace("ANGEL倶楽部", "ANGEL 倶楽部") \
        .replace("ExE", "E×E") \
        .strip()

    while os.path.isdir(new_name) :
        if info != "":
            new_name += info
            info = ""
        else:
            new_name += " [another]"
    print(folder_name.ljust(60), "->", new_name)
    os.rename(folder_name, new_name)

os.system("pause")
