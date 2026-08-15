# /// script
# requires-python = ">=3.13"
# ///
"""讀取 massigra-save-session.py 存下的工作階段檔，重新開啟所有圖（開機後跑這支）。"""
import json
import os
import subprocess
import sys
import time

# ===== 設定區 =====
DELAY_MS = 10  # 每張圖之間的開啟間隔
FALLBACK_EXE = r'D:\My Document\My Tools\MassiGra\MassiGra.exe'
SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'massigra-session.json')
# =================

# 輸出被重導向時（非真實主控台），罕見字元以 ? 取代而不是讓整支腳本炸掉
sys.stdout.reconfigure(errors='replace')


def main():
    if not os.path.isfile(SESSION_FILE):
        input('找不到工作階段檔，請先跑 massigra-save-session.py。按 Enter 關閉')
        return

    with open(SESSION_FILE, encoding='utf-8') as f:
        session = json.load(f)

    exe = session.get('exe') or FALLBACK_EXE
    if not os.path.isfile(exe):
        exe = FALLBACK_EXE

    files = session.get('files', [])
    if not files:
        input('工作階段檔裡沒有任何圖。按 Enter 關閉')
        return

    opened = 0
    for path in files:
        if not os.path.exists(path):
            print(f'[找不到] {path}')
            continue
        subprocess.Popen([exe, path])
        opened += 1
        time.sleep(DELAY_MS / 1000)


main()
