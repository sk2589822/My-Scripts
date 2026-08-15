# /// script
# requires-python = ">=3.13"
# dependencies = ["send2trash"]
# ///
"""批次用 ImageMagick 把圖片縮到最大高度。

原圖先移進該資料夾的 Original/ 暫存，縮圖成功後整個暫存資料夾丟進資源回收桶；
Original/ 已存在代表上次沒跑完，會直接接續縮圖、不再搬檔。
"""
import ctypes
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor

from send2trash import send2trash

# ===== 設定區 =====
MAX_HEIGHT = 2160
STAGING_DIR_NAME = 'Original'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
WORKERS = 6  # 同時處理幾張（16 核實測的甜蜜點，約 3.2 倍）
# =================

# magick -monitor 的進度格式：load image[路徑]: 300 of 2500, 12% complete
# 只把路徑換成短前綴，其餘訊息照 magick 原樣顯示
MONITOR_PATTERN = re.compile(
    r'^(?P<phase>[a-z ]+)\[(?P<path>.*)\]: (?P<progress>\d+ of \d+, \d+% complete)$')
REDRAW_INTERVAL = 0.05  # 重畫間隔；平行時每張圖都在回報，畫太密只會拖慢主控台
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

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

    display = Display()
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            results = list(pool.map(
                lambda pair: resize_one(staging, folder, pair[1], pair[0], len(names), display),
                enumerate(names, start=1)))
    finally:
        display.close()

    failed = [name for name, ok in zip(names, results) if not ok]
    if failed:
        print(f'[錯誤] {len(failed)} 張失敗，原圖保留在 {staging}，不丟資源回收桶。')
        return

    print(f'完成 {len(names)} 張。')
    send2trash(staging)


def resize_one(staging, folder, name, index, total, display):
    """縮一張圖，進度更新在這張圖自己那一行。回傳是否成功。

    一次只餵一張給 magick：餵萬用字元的話它會先載入全部圖片再一起縮，
    既吃記憶體，進度也會變成「全部載入→全部縮圖」而沒辦法一張一行。
    """
    process = subprocess.Popen([
        'magick', '-monitor',
        os.path.join(staging, name),
        '-resize', f'x{MAX_HEIGHT}>',
        os.path.join(folder, f'{os.path.splitext(name)[0]}-resized.jpg'),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, bufsize=0)

    prefix = f'[{index}/{total}] {name}'
    last = None
    buffer = b''
    while True:
        data = process.stderr.read(4096)
        if not data:
            break
        buffer += data
        chunks = buffer.split(b'\r')
        buffer = chunks.pop()
        for chunk in chunks:
            last = show_chunk(chunk, prefix, index, display) or last
    if buffer:
        last = show_chunk(buffer, prefix, index, display) or last

    process.wait()
    if process.returncode == 0:
        # magick 最後印的就是 100%，原樣定格
        display.finish(index, last or prefix)
        return True

    display.finish(index, f'{prefix}  失敗（exit {process.returncode}）')
    return False


def show_chunk(raw, prefix, index, display):
    """處理 magick 的一段輸出。是進度就回傳那一行，其餘回 None。

    magick 的進度走 stderr、以 \\r 分隔、字串一律是 UTF-8；自己接管解碼才不會在
    cp950 主控台變亂碼。
    """
    text = raw.decode('utf-8', errors='replace').strip()
    if not text:
        return None

    match = MONITOR_PATTERN.match(text)
    if not match:
        display.message(text)  # magick 的警告或錯誤
        return None

    line = f'{prefix}  {match["phase"]}: {match["progress"]}'
    display.update(index, line)
    return line


class Display:
    """畫面底部維持一個「進行中」區塊，跑完的檔案往上堆成永久紀錄。

    平行處理時好幾張圖同時在回報進度，而 \\r 只能回到目前這行的行首、沒辦法往上移，
    所以改用 ANSI 游標控制：每次更新就把整個區塊擦掉重畫。
    """

    def __init__(self):
        self.live = sys.stdout.isatty() and enable_ansi()
        self.active = {}
        self.drawn = 0
        self.last_draw = 0.0
        self.lock = threading.Lock()

    def update(self, index, line):
        """某張圖的進度變了"""
        with self.lock:
            if not self.live or self.active.get(index) == line:
                return
            self.active[index] = line
            if time.monotonic() - self.last_draw < REDRAW_INTERVAL:
                return  # 這次先略過，下一次更新或收尾時會一起補上
            self._redraw()

    def finish(self, index, line):
        """某張圖跑完了：把它的最後一行留成永久紀錄"""
        with self.lock:
            self.active.pop(index, None)
            self._erase()
            print(truncate(line, line_width()) if self.live else line)
            self._redraw()

    def message(self, text):
        """magick 的警告或錯誤，原樣留在畫面上"""
        with self.lock:
            self._erase()
            print(text)
            self._redraw()

    def close(self):
        with self.lock:
            self._erase()
            sys.stdout.flush()

    def _erase(self):
        if self.live and self.drawn:
            sys.stdout.write(f'\x1b[{self.drawn}A\x1b[J')
            self.drawn = 0

    def _redraw(self):
        if not self.live:
            return
        self._erase()
        for index in sorted(self.active):
            sys.stdout.write(truncate(self.active[index], line_width()) + '\n')
        self.drawn = len(self.active)
        self.last_draw = time.monotonic()
        sys.stdout.flush()


def enable_ansi():
    """Windows 主控台預設不吃 ANSI 游標控制（實測 mode 0x3），要自己打開"""
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_uint32()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return False
    return bool(kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING))


def line_width():
    return max(shutil.get_terminal_size((100, 25)).columns - 1, 20)


def truncate(text, width):
    """截到指定顯示寬度（全形字算兩格），免得長檔名折行把區塊撐爛"""
    result = ''
    used = 0
    for char in text:
        size = 2 if unicodedata.east_asian_width(char) in ('W', 'F') else 1
        if used + size > width:
            break
        result += char
        used += size
    return result


main()
