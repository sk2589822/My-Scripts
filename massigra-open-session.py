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

# 輸出被重導向時（非真實主控台）一律用 UTF-8，日文檔名才不會被 cp950 變成一排 ? 或直接炸掉
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


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
    missing = []
    for path in files:
        if not os.path.exists(path):
            missing.append(path)
            continue
        # 導掉輸出，免得看圖程式往這個主控台吐非 UTF-8 的訊息
        subprocess.Popen([exe, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        opened += 1
        time.sleep(DELAY_MS / 1000)

    # 全部開完就直接關閉；有缺檔才停住，免得清單一閃而過
    if missing:
        print(f'以下 {len(missing)} 張找不到：')
        for path in missing:
            print(f'  {path}')
        print()
        input(f'已重開 {opened}/{len(files)} 張。按 Enter 關閉')


main()
