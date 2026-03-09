import pandas as pd
import sys

def run_monitor():
    file_name = '台股-4533-協易機-價量分析.csv'
    
    try:
        # 1. 嘗試用不同的編碼讀取 (解決 Windows 產生的 CSV 編碼問題)
        try:
            df = pd.read_csv(file_name, encoding='utf-8-sig')
        except:
            df = pd.read_csv(file_name, encoding='cp950')
            
        print("✅ 檔案讀取成功！")
        
        # 2. 清理欄位名稱 (避免肉眼看不見的空格)
        df.columns = df.columns.str.strip()
        print(f"📊 偵測到的欄位有：{list(df.columns)}")

        # 3. 抓取最後一筆紀錄
        latest_data = df.iloc[-1]
        
        # 這裡用「關鍵字」去找，避免名字對不準
        date = latest_data.get('日期', '未知日期')
        close_price = latest_data.get('收盤價', 0)
        vol_ratio = latest_data.get('努力倍率 (Vol Ratio)', 0)
        intent_score = latest_data.get('意圖分數 (Close Pos %)', 0)
        status = latest_data.get('狀態', '無狀態')

        # 4. 打印診斷報告
        print(f"\n--- 🐊 詩織機器人 盤後診斷報告 ({date}) ---")
        print(f"今日收盤：{close_price} 元")
        print(f"努力倍率：{float(vol_ratio):.2f}x")
        print(f"意圖分數：{float(intent_score):.2f}")
        print(f"目前狀態：{status}")

        if float(close_price) <= 30.0:
            print("🚨 注意：已跌破 30.0 元止損位，請執行品管退料程序！")
        elif float(close_price) >= 33.8:
            print("🚀 突破：已站回 33.8 元關鍵地基，結構轉強！")
        else:
            print("☕ 觀察：目前在地基區間內震盪，繼續喝紅茶觀察。")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        sys.exit(1) # 讓 GitHub 知道出錯了

if __name__ == "__main__":
    run_monitor()
