import pandas as pd
import sys
import numpy as np
import re
import os
import requests

def send_line_message(message):
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('LINE_USER_ID')
    if not token or not user_id: return
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    data = {'to': user_id, 'messages': [{'type': 'text', 'text': message}]}
    requests.post(url, headers=headers, json=data)

def clean_value(value):
    """強效除垢：處理 $、%、逗號、換行"""
    if pd.isna(value) or value == '': return 0.0
    if isinstance(value, (int, float)): return float(value)
    # 移除所有非數字、非小數點的字元
    cleaned = re.sub(r'[^\d.]', '', str(value))
    try: return float(cleaned)
    except: return 0.0

def find_column(df, keyword):
    """模糊搜尋欄位名稱"""
    for col in df.columns:
        if keyword in col:
            return col
    return None

def run_monitor():
    file_name = '台股-4533協易機-價量分析.csv'
    try:
        df = pd.read_csv(file_name, encoding='utf-8-sig', na_values=['#DIV/0!', '#N/A', '', ' '])
        
        # 1. 抓取關鍵欄位
        col_close = find_column(df, '收盤價')
        col_vol = find_column(df, '努力')
        col_intent = find_column(df, '意圖')
        col_status = find_column(df, '狀態')

        # 2. 過濾有效數據
        valid_df = df[df[col_close].notna()]
        valid_df = valid_df[valid_df[col_close] != 0]
        
        if valid_df.empty:
            print("❌ 錯誤：找不到有效數據！")
            return
            
        latest_data = valid_df.iloc[-1]
        
        # 3. 提取數據並清理
        date = latest_data.get('日期', '未知日期')
        close_price = clean_value(latest_data.get(col_close))
        vol_ratio = clean_value(latest_data.get(col_vol))
        intent_score = clean_value(latest_data.get(col_intent))
        status = str(latest_data.get(col_status, '無狀態'))

        report = (
            f"\n--- 🐊 詩織機器人 盤後診斷報告 ({date}) ---\n"
            f"標的：4533 協易機\n"
            f"今日收盤：{close_price} 元\n"
            f"努力倍率：{vol_ratio:.2f}x\n"
            f"意圖分數：{intent_score:.2f}\n"
            f"目前狀態：{status}\n"
        )

        if close_price <= 30.0:
            report += "🚨 注意：已跌破 30.0 元止損位！"
        elif close_price >= 33.8:
            report += "🚀 突破：已站回 33.8 元關鍵地基！"
        else:
            report += "☕ 觀察：目前在地基區間內震盪，繼續喝紅茶。"

        print(report)
        send_line_message(report)

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        sys.exit(1)

if __name__ == "__main__":
    run_monitor()
