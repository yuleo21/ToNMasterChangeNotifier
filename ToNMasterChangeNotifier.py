import sys
import subprocess

def ensure_package(pkg_name):
    try:
        __import__(pkg_name)
    except ImportError:
        ans = input(f"パッケージ '{pkg_name}' が見つかりません。インストールしますか？ [y/n]: ").strip().lower()
        if ans in ('', 'y', 'yes'):
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg_name])
        else:
            print(f"'{pkg_name}' がないため実行を継続できません。")
            sys.exit(1)

ensure_package('websockets')

import asyncio
import websockets
import json
import datetime
import os
import winsound

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

WS_URI = 'ws://127.0.0.1:11398'
WAV_FILE = resource_path('MasterChanged.wav')

if not os.path.isfile(WAV_FILE):
    print(f"警告: サウンドファイルが見つかりません: {WAV_FILE}")
    sound_available = False
else:
    sound_available = True

async def watch_master_change():
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WebSocket に接続中: {WS_URI}")
    async with websockets.connect(WS_URI) as ws:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WebSocket 接続に成功しました。")
        async for msg in ws:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                continue

            if data.get('Type') == 'MASTER_CHANGE':
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{now} - マスターが変更されました。")
                if sound_available:
                    winsound.PlaySound(WAV_FILE, winsound.SND_FILENAME)
                else:
                    print("サウンド再生が利用できません。")

if __name__ == '__main__':
    print("=== ToN Master Change Notifier ===")
    while True:
        try:
            asyncio.run(watch_master_change())
        except Exception as e:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{now} - WebSocket 接続に失敗しました: {e}")
            print("ToN Save Manager を起動し、「WebSocket API サーバー」を有効にしてください。")

        try:
            input("再接続を試みるには Enter キーを押してください。終了するには Ctrl+C を押してください...")
        except KeyboardInterrupt:
            break
