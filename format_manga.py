import re
import os

dir_path = r'D:\N'
storage_path = r'G:\EX-II\漫'

def main():
    ensure = input('Enter "1" to rename or else to preview the results: ') == '1'

    manga_list = os.listdir(storage_path)

    for folder_name in os.listdir(dir_path):
        # Ignore non-folder.
        if not os.path.isdir(os.path.join(dir_path, folder_name)):
            continue

        # Ignore folder which is not matched.
        if not re.search('^(\(.*?\))? ?\[.*?\].*?$', folder_name):
            continue

        folder_name_without_info, info = split_folder_name_and_info(folder_name)
        author, title = get_author_and_title(folder_name_without_info)
        existing_mangas = [folder_name for folder_name in manga_list if folder_name.startswith(author + '　')]
        new_index = 0

        for existing_folder_name in existing_mangas:
            existing_folder_name_temp = re.sub('\(\d+\)', "", existing_folder_name)
            existing_author, existing_title = existing_folder_name_temp.split('　', 1)
            # If the folder is existing in storage_path
            if existing_author == author and existing_title == title:
                new_folder_name = existing_folder_name + ' [another]'
                break
        else:
            new_index = get_new_index(existing_mangas)
            new_folder_name = get_new_folder_name(author, title, new_index)

        new_folder_name = add_info_if_duplicate(new_folder_name, info)

        rename_folder(folder_name, new_folder_name, dir_path, ensure)
        rename_existing_folder(new_index, existing_mangas, ensure)

    os.system('pause')

def split_folder_name_and_info(folder_name):
    folder_name_without_info = re.sub(' ?((\[(\d{6,7}|DL.|別.*)\])|( \+ .*))*$', '', folder_name, flags=re.IGNORECASE)
    info = re.sub('\[\d{6,7}\]$', '', folder_name.replace(folder_name_without_info, ''))
    return folder_name_without_info, info


def get_author_and_title(folder_name):
    match = re.match('^(\(.*?\))? ?\[(?P<author>.*?)\] ?(?P<title>.*?)$',
        folder_name,
        flags=re.IGNORECASE)
    return match.group('author'), match.group('title')


def get_new_index(existing_mangas):
    indexes = []
    for folder_name in existing_mangas:
        search = re.search('　\((\d+)\)', folder_name);
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
    while os.path.isdir(new_folder_name) :
        if info != '':
            new_folder_name += info
            info = ''
        else:
            new_folder_name += ' [another]'
    return new_folder_name


def rename_folder(old_name, new_name, path, ensure):
    os.chdir(path)
    print(old_name.ljust(40), '\t->', new_name)

    if ensure == True:
        os.rename(old_name, new_name)


def rename_existing_folder(new_index, existing_mangas, ensure):
    if new_index == 2:
        author, title = existing_mangas[0].split('　', 1)
        rename_folder(existing_mangas[0], get_new_folder_name(author, title, 1), storage_path, ensure)

main()