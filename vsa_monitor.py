import pandas as pd
import sys
import numpy as np
import re

def clean_value(value):
    """清理包含 $、%、逗號或空格的字串"""
    if pd.isna(value) or value == '':
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    # 去除所有非數字、非小數點的字元
    cleaned = re.sub(r'[^\d.]', '', str(value))
    try:
        return float(cleaned)
    except:
        return 0.0

def run_monitor():
    file_name = '台股-4533協易機-價量分析.csv'
    
    try:
        # 1. 讀取檔案
        df = pd.read_csv(file_name, encoding='utf-8-sig', na_values=['#DIV/0!', '#N/A', '', ' '])
        
        # 2. 清理欄位名稱：移除換行符號、空格
        df.columns = df.columns.str.replace('\n', ' ').str.strip()
        print(f"✅ 偵測到欄位：{list(df.columns)}")

        # 3. 過濾掉無效行：必須要有「日期」且「收盤價」不是 0
        df = df[df['日期'].notna()]
        
        # 4. 定義要清理的目標欄位 (根據你的 CSV 標頭)
        target_cols = {
            'close': '收盤價',
            'vol_ratio': '努力倍率 (Vol Ratio)',
            'intent': '意圖分數 (Close Pos %)'
        }

        # 5. 抓取最後一筆有效紀錄
        # 我們先找到最後一行有「日期」的，再往回找直到有「收盤價」
        valid_rows = df[df['收盤價'].notna()]
        if valid_rows.empty:
            print("❌ 錯誤：找不到任何包含有效數據的行！")
            return
            
        latest_data = valid_rows.iloc[-1]
        
        date = latest_data.get('日期', '未知日期')
        close_price = clean_value(latest_data.get(target_cols['close']))
        vol_ratio = clean_value(latest_data.get(target_cols['vol_ratio']))
        intent_score = clean_value(latest_data.get(target_cols['intent']))
        status = str(latest_data.get('狀態', '無狀態'))

        print(f"\n--- 🐊 詩織機器人 盤後診斷報告 ({date}) ---")
        print(f"今日收盤：{close_price} 元")
        print(f"努力倍率：{vol_ratio:.2f}x")
        print(f"意圖分數：{intent_score:.2f}")
        print(f"目前狀態：{status}")

        # 邏輯判斷
        if close_price <= 30.0:
            print("🚨 注意：已跌破 30.0 元止損位，請執行品管退料程序！")
        elif close_price >= 33.8:
            print("🚀 突破：已站回 33.8 元關鍵地基，結構轉強！")
        else:
            print("☕ 觀察：目前在地基區間內震盪，繼續喝紅茶觀察。")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        sys.exit(1)

if __name__ == "__main__":
    run_monitor()
