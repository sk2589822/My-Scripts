# /// script
# requires-python = ">=3.13"
# ///
import os
import re

# ===== 設定區 =====
DIR_PATH = r'D:\M'             # 待整理區
STORAGE_PATH = r'G:\EX-II\漫'  # 收藏庫
# =================


def main():
    ensure = input('輸入「1」執行改名，其他鍵只預覽結果：') == '1'

    manga_list = os.listdir(STORAGE_PATH)

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

        new_folder_name = add_info_if_duplicate(new_folder_name, info)

        rename_folder(folder_name, new_folder_name, DIR_PATH, ensure)
        rename_existing_folder(new_index, existing_mangas, ensure)

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


def add_info_if_duplicate(new_folder_name, info):
    # 名字必須在待整理區與收藏庫兩邊都唯一：
    # 待整理區唯一是為了改名本身不撞，收藏庫唯一是為了之後搬進去不撞
    while (os.path.isdir(os.path.join(DIR_PATH, new_folder_name))
           or os.path.isdir(os.path.join(STORAGE_PATH, new_folder_name))):
        if info != '':
            new_folder_name += info
            info = ''
        else:
            new_folder_name += ' [another]'
    return new_folder_name


def rename_folder(old_name, new_name, path, ensure):
    print(old_name.ljust(40), '\t->', new_name)

    if ensure:
        os.rename(os.path.join(path, old_name), os.path.join(path, new_name))


def rename_existing_folder(new_index, existing_mangas, ensure):
    if new_index == 2:
        author, title = existing_mangas[0].split('　', 1)
        rename_folder(existing_mangas[0], get_new_folder_name(author, title, 1), STORAGE_PATH, ensure)


main()
