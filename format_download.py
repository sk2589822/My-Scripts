import re
import os
import pathlib

ROOT = r"F:\EX\J"
os.chdir(ROOT)

for folder_name in os.listdir(ROOT):
    if not os.path.isdir(os.path.join(ROOT, folder_name)):
      continue

    pattern = r"^(\(同人.*?\))?(?P<event>\(.*?\))? ?\[(?P<author>.*?)\] ?(?P<work>.*?) ?(\(オリジナル\))?(?P<original_work>\(.*\))? ?(?P<dl_tag>\[DL版\])? ?(?P<note>\(.*?\))?$"
    matches = re.search(pattern, folder_name)

    if not matches:
      continue
    
    author = matches.group('author')
    work = matches.group('work')

    if author == "" or work == "":
      continue

    event = matches.group('event')
    original_work = matches.group('original_work')
    dl_tag = matches.group('dl_tag')
    note = matches.group('note')

    new_folder_name = work

    if (original_work):
      new_folder_name += f" {original_work}"

    if (note):
      new_folder_name += f" {note}"

    if (event):
      new_folder_name += f" {event}"

    pathlib.Path(author).mkdir(parents=True, exist_ok=True)
    new_folder_path = os.path.join(ROOT, author, new_folder_name)

    while os.path.isdir(new_folder_path) :
      if (dl_tag):
        new_folder_path += f" {dl_tag}"
      else:
        new_folder_path += " [another]"

    print(f"From: \t {folder_name}")
    print(f"To: \t {new_folder_path.replace(ROOT, '')}")

    os.rename(folder_name, new_folder_path)

os.system("pause")
