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
import re
import shutil
import subprocess
import sys
import unicodedata

from send2trash import send2trash

# ===== 設定區 =====
MAX_HEIGHT = 2160
STAGING_DIR_NAME = 'Original'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
# =================

# magick -monitor 的進度格式：load image[路徑]: 300 of 2500, 12% complete
# 只把路徑換成短前綴，其餘訊息照 magick 原樣顯示
MONITOR_PATTERN = re.compile(
    r'^(?P<phase>[a-z ]+)\[(?P<path>.*)\]: (?P<progress>\d+ of \d+, \d+% complete)$')

# 輸出被重導向時（非真實主控台）一律用 UTF-8，日文檔名才不會被 cp950 變成一排 ? 或直接炸掉
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


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

    names = sorted(name for name in os.listdir(staging)
                   if os.path.isfile(os.path.join(staging, name)))

    failed = []
    for index, name in enumerate(names, start=1):
        if not resize_one(staging, folder, name, index, len(names)):
            failed.append(name)

    if failed:
        print(f'[錯誤] {len(failed)} 張失敗，原圖保留在 {staging}，不丟資源回收桶。')
        return

    print(f'完成 {len(names)} 張。')
    send2trash(staging)


def resize_one(staging, folder, name, index, total):
    """縮一張圖，進度就地更新在這張圖自己那一行。回傳是否成功。

    一次只餵一張給 magick：餵萬用字元的話它會先載入全部圖片再一起縮，
    既吃記憶體，進度也會變成「全部載入→全部縮圖」而沒辦法一張一行。
    """
    process = subprocess.Popen([
        'magick', '-monitor',
        os.path.join(staging, name),
        '-resize', f'x{MAX_HEIGHT}>',
        os.path.join(folder, f'{os.path.splitext(name)[0]}-resized.jpg'),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, bufsize=0)

    # magick 的進度走 stderr、以 \r 分隔、字串一律是 UTF-8；自己接管解碼才不會在
    # cp950 主控台變亂碼，也才能把長路徑換成短標籤、不讓它換行洗版
    prefix = f'[{index}/{total}] {name}'
    state = {'last_line': None, 'live': sys.stdout.isatty()}
    buffer = b''
    while True:
        data = process.stderr.read(4096)
        if not data:
            break
        buffer += data
        chunks = buffer.split(b'\r')
        buffer = chunks.pop()
        for chunk in chunks:
            show_monitor_output(chunk, prefix, state)
    if buffer:
        show_monitor_output(buffer, prefix, state)

    process.wait()
    if process.returncode == 0:
        keep_line(prefix, state)
        return True

    replace_line(f'{prefix}  失敗（exit {process.returncode}）', state)
    return False


def show_monitor_output(raw, prefix, state):
    text = raw.decode('utf-8', errors='replace').strip()
    if not text:
        return

    match = MONITOR_PATTERN.match(text)
    if not match:
        # 不是進度，就是 magick 的警告或錯誤，要留在畫面上
        if state['last_line'] is not None:
            clear_line()
            state['last_line'] = None
        print(text)
        return

    # 進度只在真的主控台上畫；被重導向時那些 \r 只會變成一大堆垃圾
    if not state['live']:
        return

    line = f'{prefix}  {match["phase"]}: {match["progress"]}'
    if line != state['last_line']:
        state['last_line'] = line
        write_line(line)


def keep_line(prefix, state):
    """成功收尾：magick 最後印的就是 100%，原封不動定格在這一行"""
    if state['last_line'] is None:
        # magick 沒回報過進度（圖太小），或輸出被重導向
        print(prefix)
    else:
        sys.stdout.write('\n')
        sys.stdout.flush()
    state['last_line'] = None


def replace_line(text, state):
    """失敗收尾：把停在半途的進度換成失敗訊息"""
    if state['live'] and state['last_line'] is not None:
        write_line(text)
        sys.stdout.write('\n')
        sys.stdout.flush()
    else:
        print(text)
    state['last_line'] = None


def write_line(text):
    sys.stdout.write('\r' + fit(text, line_width()))
    sys.stdout.flush()


def clear_line():
    sys.stdout.write('\r' + ' ' * line_width() + '\r')
    sys.stdout.flush()


def line_width():
    return max(shutil.get_terminal_size((100, 25)).columns - 1, 20)


def fit(text, width):
    """截斷並補滿到指定顯示寬度（全形字算兩格），免得殘留上一行的尾巴"""
    result = ''
    used = 0
    for char in text:
        size = 2 if unicodedata.east_asian_width(char) in ('W', 'F') else 1
        if used + size > width:
            break
        result += char
        used += size
    return result + ' ' * (width - used)


main()
