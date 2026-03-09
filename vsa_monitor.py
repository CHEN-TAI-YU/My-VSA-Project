import pandas as pd
import sys
import numpy as np

def run_monitor():
    file_name = '台股-4533協易機-價量分析.csv'
    
    try:
        # 1. 讀取檔案，並將 Excel 常見錯誤字眼視為缺失值 (NaN)
        df = pd.read_csv(file_name, encoding='utf-8-sig', na_values=['#DIV/0!', '#N/A', '', ' '])
        
        # 2. 清理：刪除完全空白的列，並修剪欄位空格
        df = df.dropna(how='all')
        df.columns = df.columns.str.strip()
        
        # 3. 抓取「最後一筆有數據」的紀錄
        latest_data = df.iloc[-1]
        
        # 4. 資料轉換與清理 (將無法轉換的變成 0)
        def clean_num(val):
            try:
                v = float(val)
                return 0 if np.isnan(v) else v
            except:
                return 0

        date = latest_data.get('日期', '未知日期')
        close_price = clean_num(latest_data.get('收盤價'))
        vol_ratio = clean_num(latest_data.get('努力倍率 (Vol Ratio)'))
        intent_score = clean_num(latest_data.get('意圖分數 (Close Pos %)'))
        status = str(latest_data.get('狀態', '無狀態'))

        print(f"\n--- 🐊 詩織機器人 盤後診斷報告 ({date}) ---")
        
        # 如果收盤價是 0，代表這行資料可能還沒填好
        if close_price == 0:
            print("⚠️ 警告：最後一行資料似乎不完整，請檢查 CSV 內容！")
            return

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
