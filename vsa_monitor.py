import pandas as pd
import sys
import numpy as np

def run_monitor():
    file_name = '台股-4533協易機-價量分析.csv'
    
    try:
        # 1. 讀取檔案，將 Excel 常見錯誤字眼視為 NaN
        df = pd.read_csv(file_name, encoding='utf-8-sig', na_values=['#DIV/0!', '#N/A', '', ' '])
        
        # 2. 清理：去掉欄位空格
        df.columns = df.columns.str.strip()
        
        # 3. 【核心修正】過濾掉所有「收盤價」是空的或是 0 的無效行
        # 這樣機器人就會自動忽略你預留的空白表格
        valid_df = df.dropna(subset=['收盤價'])
        valid_df = valid_df[valid_df['收盤價'] != 0]

        if valid_df.empty:
            print("❌ 錯誤：CSV 檔案中找不到任何有效的收盤價數據！")
            return

        # 4. 抓取「最後一筆有效」紀錄
        latest_data = valid_df.iloc[-1]
        
        date = latest_data.get('日期', '未知日期')
        close_price = float(latest_data.get('收盤價', 0))
        vol_ratio = float(latest_data.get('努力倍率 (Vol Ratio)', 0))
        intent_score = float(latest_data.get('意圖分數 (Close Pos %)', 0))
        status = str(latest_data.get('狀態', '無狀態'))

        print(f"\n--- 🐊 詩織機器人 盤後診斷報告 ({date}) ---")
        print(f"今日收盤：{close_price} 元")
        print(f"努力倍率：{vol_ratio:.2f}x")
        print(f"意圖分數：{intent_score:.2f}")
        print(f"目前狀態：{status}")

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
