import pandas as pd

# 1. 讀取你的 CSV 檔案
df = pd.read_csv('台股-4533-協易機.csv')

# 2. 抓取最後一筆紀錄 (今天的數據)
latest_data = df.iloc[-1]

date = latest_data['日期']
close_price = latest_data['收盤價']
vol_ratio = latest_data['努力倍率 (Vol Ratio)']
intent_score = latest_data['意圖分數 (Close Pos %)']
status = latest_data['狀態']

# 3. 模擬機器人診斷邏輯
print(f"--- 🐊 詩織機器人 盤後診斷報告 ({date}) ---")
print(f"標的：4533 協易機")
print(f"今日收盤：{close_price} 元")
print(f"努力倍率：{vol_ratio:.2f}x (是否異動？)")
print(f"意圖分數：{intent_score:.2f} (大鱷護盤力道)")
print(f"目前狀態：{status}")

# 4. 簡單的風險警示
if close_price <= 30.0:
    print("🚨 注意：已跌破 30.0 元止損位，請執行品管退料程序！")
elif close_price >= 33.8:
    print("🚀 突破：已站回 33.8 元關鍵地基，結構轉強！")
else:
    print("☕ 觀察：目前在地基區間內震盪，繼續喝紅茶觀察。")
