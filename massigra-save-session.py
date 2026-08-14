# /// script
# requires-python = ">=3.13"
# dependencies = ["pywin32"]
# ///
"""把 MassiGra 目前開著的所有圖存成工作階段檔（關機前跑這支）。

之後用 massigra-open-session.py 重新開啟全部。
"""
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

# 輸出被重導向時（非真實主控台），罕見字元以 ? 取代而不是讓整支腳本炸掉
sys.stdout.reconfigure(errors='replace')


def main():
    windows = list_massigra_windows()

    # 視窗標題去掉結尾的「 (n/m) ...」就是圖檔路徑
    paths = [path for path in
             (re.sub(r'\s*\(\d+/\d+\).*$', '', title) for _, title, _ in windows)
             if path]

    if not paths:
        input('MassiGra 目前沒有開著任何圖。按 Enter 關閉')
        return

    for path in paths:
        print(path)

    session = {
        'exe': windows[0][2],
        'saved_at': datetime.now().isoformat(timespec='seconds'),
        'files': paths,
    }
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(session, f, ensure_ascii=False, indent=2)

    print()
    input(f'共 {len(paths)} 張，已存到 {os.path.basename(SESSION_FILE)}。按 Enter 關閉')


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
