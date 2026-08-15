# /// script
# requires-python = ">=3.13"
# ///
"""批次統一 .ass 字幕樣式，並把影片檔名對齊字幕檔名（讓播放器自動載入字幕）。

改完的字幕放原地；原始字幕移進同資料夾的 subtitle-backup/。
subtitle-backup/ 已有同名備份的字幕視為處理過，跳過。
"""
import os
import re
import shutil
import sys

# ===== 設定區 =====
BACKUP_DIR_NAME = 'subtitle-backup'
DEFAULT_STYLE = ('Style: Default,Microsoft YaHei,38,&H00FFFFFF,&HF0000000,&H00800080,&HF0000000,'
                 '-1,0,0,0,100,100,0,0,1,1,0,2,30,30,10,134')
REMOVED_STYLE_NAMES = ['Default', '魔穗体', 'maho', 'Maho', 'Taka-Default', 'Sub-CN', 'Sub-CH']
# =================

# 輸出被重導向時（非真實主控台）一律用 UTF-8，日文檔名才不會被 cp950 變成一排 ? 或直接炸掉
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def main():
    folder = input('輸入資料夾路徑：').strip().strip('"')
    if not os.path.isdir(folder):
        input('找不到這個資料夾。按 Enter 關閉')
        return

    process_folder(folder)
    input('按 Enter 關閉')


def process_folder(folder):
    backup_dir = os.path.join(folder, BACKUP_DIR_NAME)
    files = os.listdir(folder)
    ass_files = [name for name in files if name.lower().endswith('.ass')]
    if not ass_files:
        print('這個資料夾裡沒有 .ass 字幕檔。')
        return

    for ass_name in ass_files:
        backup_path = os.path.join(backup_dir, ass_name)
        if os.path.exists(backup_path):
            print(f'[跳過] {ass_name}（subtitle-backup 已有備份）')
            continue

        ass_path = os.path.join(folder, ass_name)
        with open(ass_path, 'rb') as f:
            raw = f.read()
        had_bom = raw.startswith(b'\xef\xbb\xbf')
        try:
            text = raw.decode('utf-8-sig')
        except UnicodeDecodeError:
            print(f'[跳過] {ass_name}（不是 UTF-8 編碼，不敢動）')
            continue

        formatted = format_ass(text)

        os.makedirs(backup_dir, exist_ok=True)
        shutil.move(ass_path, backup_path)
        # newline='' 保留字幕原本的換行符號，不做轉換
        with open(ass_path, 'w', encoding='utf-8-sig' if had_bom else 'utf-8', newline='') as f:
            f.write(formatted)
        print(f'[格式化] {ass_name}')

        rename_video(folder, files, ass_name)


def format_ass(text):
    nl = '\r\n' if '\r\n' in text else '\n'

    # 移除既有的預設樣式行（每個名稱只移除第一個，與原版行為一致）
    for name in REMOVED_STYLE_NAMES:
        text = re.sub(rf'^Style: ?{re.escape(name)} ?,[^\r\n]*', '', text, count=1, flags=re.M)

    # 在 Format 行後面插入統一的 Default 樣式
    text = re.sub(r'^(Format: Name, Fontname[^\r\n]*)',
                  lambda m: m.group(1) + nl + nl + DEFAULT_STYLE,
                  text, count=1, flags=re.M)

    text = re.sub(r'^PlayResX: ?\d+', 'PlayResX: 1280', text, count=1, flags=re.M)
    text = re.sub(r'^PlayResY: ?\d+', 'PlayResY: 720', text, count=1, flags=re.M)
    text = re.sub(r'^ScaledBorderAndShadow: ?yes(?=\r?$)', 'ScaledBorderAndShadow: no',
                  text, count=1, flags=re.M)
    text = re.sub(r'^Style: Taka-Default -High,方正粗圆_GBK,38,&H00FFFFFF,&H00FFFFFF,&H008140FF,&H96000000',
                  'Style: Default,Microsoft YaHei,38,&H00FFFFFF,&HF0000000,&H00800080,&HF0000000',
                  text, count=1, flags=re.M)
    return text


def rename_video(folder, files, ass_name):
    base_name = ass_name[:-len('.ass')]
    video_name = next((name for name in files if name != ass_name and base_name in name), None)
    if not video_name:
        return

    ext = os.path.splitext(video_name)[1]
    if not ext:
        return

    target = f'{base_name}{ext}'
    if video_name == target:
        return

    try:
        os.rename(os.path.join(folder, video_name), os.path.join(folder, target))
        print(f'[影片改名] {video_name} -> {target}')
    except OSError as error:
        print(f'[影片改名失敗] {video_name}：{error}')


main()
