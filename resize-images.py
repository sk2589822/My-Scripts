# /// script
# requires-python = ">=3.13"
# dependencies = ["send2trash"]
# ///
"""批次用 ImageMagick 把圖片縮到最大高度。

原圖先移進該資料夾的 Original/ 暫存，縮圖成功後整個暫存資料夾丟進資源回收桶；
Original/ 已存在代表上次沒跑完，會直接接續縮圖、不再搬檔。
"""
import fnmatch
import os
import shutil
import subprocess
import sys

from send2trash import send2trash

# ===== 設定區 =====
MAX_HEIGHT = 2160
STAGING_DIR_NAME = 'Original'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
# =================

# 輸出被重導向時（非真實主控台），罕見字元以 ? 取代而不是讓整支腳本炸掉
sys.stdout.reconfigure(errors='replace')


def main():
    while True:
        input_path = input('資料夾路徑（可用逗號分隔多個，空白結束）：').strip()
        if not input_path:
            break

        name_pattern = input('檔名樣式（預設 *）：').strip() or '*'
        recursive = input('處理所有子資料夾？(y/N)：').strip().lower() in ('y', '1')

        for folder in resolve_folders(input_path, recursive):
            process_folder(folder, name_pattern)

        print('Done!')


def resolve_folders(input_path, recursive):
    if recursive:
        root = input_path.strip('"')
        if not os.path.isdir(root):
            print(f'[找不到] {root}')
            return []

        folders = [os.path.join(root, name) for name in os.listdir(root)
                   if os.path.isdir(os.path.join(root, name)) and name != STAGING_DIR_NAME]
        # 根目錄自己有散圖（或沒有任何子資料夾）時，根目錄也處理
        has_loose_images = any(
            os.path.isfile(os.path.join(root, name))
            and os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
            for name in os.listdir(root))
        if has_loose_images or not folders:
            folders.append(root)
        return folders

    folders = []
    for part in input_path.split(','):
        path = part.strip().strip('"')
        if not path:
            continue
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if not os.path.isdir(path):
            print(f'[找不到] {path}')
            continue
        if path not in folders:
            folders.append(path)
    return folders


def process_folder(folder, name_pattern):
    print(f'--- {folder} ---')
    staging = os.path.join(folder, STAGING_DIR_NAME)

    if not os.path.isdir(staging):
        targets = [name for name in os.listdir(folder)
                   if os.path.isfile(os.path.join(folder, name))
                   and os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
                   and fnmatch.fnmatch(name, f'{name_pattern}.*')]
        if not targets:
            print('沒有符合的圖片，跳過。')
            return

        os.makedirs(staging)
        for name in targets:
            shutil.move(os.path.join(folder, name), os.path.join(staging, name))

    result = subprocess.run([
        'magick', '-monitor',
        os.path.join(staging, '*'),
        '-resize', f'x{MAX_HEIGHT}>',
        '-set', 'filename:name', '%t',
        os.path.join(folder, '%[filename:name]-resized.jpg'),
    ])
    if result.returncode != 0:
        print(f'[錯誤] magick 失敗（exit {result.returncode}），原圖保留在 {staging}，不丟資源回收桶。')
        return

    send2trash(staging)


main()
