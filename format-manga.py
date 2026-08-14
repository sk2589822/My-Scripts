# /// script
# requires-python = ">=3.13"
# ///
import os
import re
import sys

# ===== 設定區 =====
DIR_PATH = r'D:\M'             # 待整理區
STORAGE_PATH = r'G:\EX-II\漫'  # 收藏庫
# =================

# 輸出被重導向時（非真實主控台），罕見字元以 ? 取代而不是讓整支腳本炸掉
sys.stdout.reconfigure(errors='replace')


def main():
    manga_list = os.listdir(STORAGE_PATH)

    planned_names = set()   # 本批已規劃占用的新名字（預覽階段還沒真的改名，要靠這份名單防同批撞名）
    operations = []         # (基準路徑, 舊名, 新名)

    for folder_name in os.listdir(DIR_PATH):
        # 只處理資料夾
        if not os.path.isdir(os.path.join(DIR_PATH, folder_name)):
            continue

        # 只處理符合下載命名格式的資料夾
        if not re.search(r'^(\(.*?\))? ?\[.*?\].*?$', folder_name):
            continue

        folder_name_without_info, info = split_folder_name_and_info(folder_name)
        author, title = get_author_and_title(folder_name_without_info)
        existing_mangas = [name for name in manga_list if name.startswith(author + '　')]
        new_index = 0

        for existing_folder_name in existing_mangas:
            existing_folder_name_temp = re.sub(r'\(\d+\)', '', existing_folder_name)
            existing_author, existing_title = existing_folder_name_temp.split('　', 1)
            # 收藏庫已有同一作品
            if existing_author == author and existing_title == title:
                new_folder_name = existing_folder_name + ' [another]'
                break
        else:
            new_index = get_new_index(existing_mangas)
            new_folder_name = get_new_folder_name(author, title, new_index)

        new_folder_name = add_info_if_duplicate(new_folder_name, info, planned_names)
        planned_names.add(new_folder_name)
        operations.append((DIR_PATH, folder_name, new_folder_name))

        # 作者出現第二部作品時，第一部要回頭補 (1)
        if new_index == 2 and (STORAGE_PATH, existing_mangas[0]) not in {(op[0], op[1]) for op in operations}:
            existing_author, existing_title = existing_mangas[0].split('　', 1)
            renamed = get_new_folder_name(existing_author, existing_title, 1)
            planned_names.add(renamed)
            operations.append((STORAGE_PATH, existing_mangas[0], renamed))

    if not operations:
        input('沒有需要改名的資料夾。按 Enter 關閉')
        return

    for _, old_name, new_name in operations:
        print(old_name.ljust(40), '\t->', new_name)

    print()
    if input('確認無誤請直接按 Enter 執行改名（輸入任意文字則取消）：') == '':
        for base_path, old_name, new_name in operations:
            os.rename(os.path.join(base_path, old_name), os.path.join(base_path, new_name))
        print(f'完成，共改名 {len(operations)} 個資料夾。')
    else:
        print('已取消，未做任何改動。')

    input('按 Enter 關閉')


def split_folder_name_and_info(folder_name):
    folder_name_without_info = re.sub(r' ?((\[(\d{6,7}|DL.|別.*)\])|( \+ .*))*$', '', folder_name, flags=re.IGNORECASE)
    info = re.sub(r'\[\d{6,7}\]$', '', folder_name.replace(folder_name_without_info, ''))
    return folder_name_without_info, info


def get_author_and_title(folder_name):
    match = re.match(r'^(\(.*?\))? ?\[(?P<author>.*?)\] ?(?P<title>.*?)$',
        folder_name,
        flags=re.IGNORECASE)
    return match.group('author'), match.group('title')


def get_new_index(existing_mangas):
    indexes = []
    for folder_name in existing_mangas:
        search = re.search(r'　\((\d+)\)', folder_name)
        if search:
            index = int(search.group(1))
            indexes.append(index)

    if not existing_mangas:
        return 0
    if not indexes:
        return 2
    else:
        return max(indexes) + 1


def get_new_folder_name(author, title, new_index):
    if new_index == 0:
        return f'{author}　{title}'
    else:
        return f'{author}　({new_index}){title}'


def add_info_if_duplicate(new_folder_name, info, planned_names):
    # 名字必須在待整理區與收藏庫兩邊都唯一：
    # 待整理區唯一是為了改名本身不撞，收藏庫唯一是為了之後搬進去不撞
    while (new_folder_name in planned_names
           or os.path.isdir(os.path.join(DIR_PATH, new_folder_name))
           or os.path.isdir(os.path.join(STORAGE_PATH, new_folder_name))):
        if info != '':
            new_folder_name += info
            info = ''
        else:
            new_folder_name += ' [another]'
    return new_folder_name


main()
