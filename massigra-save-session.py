# /// script
# requires-python = ">=3.13"
# dependencies = ["pywin32"]
# ///
"""把 MassiGra 目前開著的所有圖存成工作階段檔（關機前跑這支）。

之後用 massigra-open-session.py 重新開啟全部。
"""
import ctypes
import json
import os
import re
import sys
from datetime import datetime

import win32api
import win32con
import win32gui
import win32process

# ===== 設定區 =====
PROCESS_NAME = 'massigra.exe'
SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'massigra-session.json')
# =================

ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
REMOVED_STYLE = '\x1b[97;41m'  # 白字紅底
ADDED_STYLE = '\x1b[97;42m'    # 白字綠底
RESET_STYLE = '\x1b[0m'

# 輸出被重導向時（非真實主控台）一律用 UTF-8，日文檔名才不會被 cp950 變成一排 ? 或直接炸掉
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def main():
    windows = list_massigra_windows()

    # 視窗標題去掉結尾的「 (n/m) ...」就是圖檔路徑
    paths = [path for path in
             (re.sub(r'\s*\(\d+/\d+\).*$', '', title) for _, title, _ in windows)
             if path]

    if not paths:
        input('MassiGra 目前沒有開著任何圖。按 Enter 關閉')
        return

    saved_at, old_paths = load_saved_session()
    removed = [path for path in old_paths if path not in paths]
    added = [path for path in paths if path not in old_paths]

    if saved_at:
        print(f'跟 {saved_at} 存的工作階段（{len(old_paths)} 張）比較：')
    colored = enable_ansi()
    for path in removed:
        print(highlight(f'  - {path}', REMOVED_STYLE, colored))
    for path in added:
        print(highlight(f'  + {path}', ADDED_STYLE, colored))
    if not removed and not added:
        print('  沒有變動')
    print()

    # 只有新增不會弄丟東西，直接存；有減少才要確認，免得開錯時把舊的覆蓋掉
    if removed:
        try:
            input(f'會少掉 {len(removed)} 張。按 Enter 存檔，直接關掉視窗或 Ctrl+C 取消')
        except (KeyboardInterrupt, EOFError):
            return

    session = {
        'exe': windows[0][2],
        'saved_at': datetime.now().isoformat(timespec='seconds'),
        'files': paths,
    }
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(session, f, ensure_ascii=False, indent=2)

    input(f'共 {len(paths)} 張，已存到 {os.path.basename(SESSION_FILE)}。按 Enter 關閉')


def load_saved_session():
    """讀現有的工作階段檔 → (存檔時間, 圖檔路徑清單)；沒有或讀不懂就當作空的"""
    try:
        with open(SESSION_FILE, encoding='utf-8') as f:
            saved = json.load(f)
        return saved.get('saved_at', ''), list(saved['files'])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return '', []


def highlight(text, style, colored):
    return f'{style}{text}{RESET_STYLE}' if colored else text


def enable_ansi():
    """Windows 主控台預設不吃 ANSI 色碼，要自己打開；不是真實主控台（被重導向）就回 False 不上色"""
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_uint32()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return False
    return bool(kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING))


def list_massigra_windows():
    """列出 MassiGra 各行程的主視窗，依行程啟動時間排序 → [(啟動時間, 視窗標題, exe 路徑)]"""
    results = []
    seen_pids = set()

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in seen_pids:
            return True

        try:
            handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
        except win32api.error:
            return True
        try:
            exe = win32process.GetModuleFileNameEx(handle, 0)
            started_at = win32process.GetProcessTimes(handle)['CreationTime']
        except win32api.error:
            return True
        finally:
            handle.Close()

        if os.path.basename(exe).lower() == PROCESS_NAME:
            seen_pids.add(pid)
            results.append((started_at, title, exe))
        return True

    win32gui.EnumWindows(callback, None)
    results.sort(key=lambda item: item[0])
    return results


main()
