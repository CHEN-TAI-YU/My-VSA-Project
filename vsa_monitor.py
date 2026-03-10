import pandas as pd
import sys
import numpy as np
import re
import os
import requests

def send_line_message(message):
    """發送 LINE 訊息功能"""
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('LINE_USER_ID')
    if not token or not user_id:
        print("⚠️ 未偵測到 LINE 金鑰，跳過發送訊息。")
        return

    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'to': user_id,
        'messages': [{'type': 'text', 'text': message}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ LINE 訊息發送成功！")
    else:
        print(f"❌ LINE 發送失敗：{response.text}")

def clean_value(value):
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, (int, float)): return float(value)
    cleaned = re.sub(r'[^\d.]', '', str(value))
    try: return float(cleaned)
    except: return 0.0

def run_monitor():
    file_name = '台股-4533協易機-價量分析.csv'
    try:
        df = pd.read_csv(file_name, encoding='utf-8-sig', na_values=['#DIV/0!', '#N/A', '', ' '])
        df.columns = df.columns.str.replace('\n', ' ').str.strip()
        
        valid_rows = df[df['收盤價'].notna()]
        if valid_rows.empty:
            print("❌ 錯誤：找不到有效數據！")
            return
            
        latest_data = valid_rows.iloc[-1]
        date = latest_data.get('日期', '未知日期')
        close_price = clean_value(latest_data.get('收盤價'))
        vol_ratio = clean_value(latest_data.get('努力倍率 (Vol Ratio)'))
        intent_score = clean_value(latest_data.get('意圖分數 (Close Pos %)'))
        status = str(latest_data.get('狀態', '無狀態'))

        # 組裝報告內容
        report = (
            f"\n--- 🐊 詩織機器人 盤後診斷報告 ({date}) ---\n"
            f"標的：4533 協易機\n"
            f"今日收盤：{close_price} 元\n"
            f"努力倍率：{vol_ratio:.2f}x\n"
            f"意圖分數：{intent_score:.2f}\n"
            f"目前狀態：{status}\n"
        )

        if close_price <= 30.0:
            report += "🚨 注意：已跌破 30.0 元止損位，請執行品管退料程序！"
        elif close_price >= 33.8:
            report += "🚀 突破：已站回 33.8 元關鍵地基，結構轉強！"
        else:
            report += "☕ 觀察：目前在地基區間內震盪，繼續喝紅茶觀察。"

        print(report)
        send_line_message(report) # 啟動發送功能

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        sys.exit(1)

if __name__ == "__main__":
    run_monitor()
