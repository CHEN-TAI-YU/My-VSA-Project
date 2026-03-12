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

def get_vsa_status(g, h, i):
    """泰宇的 VSA 大鱷感測器 V2.1 核心大腦"""
    if g > 1.2 and h > 0.03 and i > 0.7:
        return "🚀 【買入/追擊】大鱷表態，補齊第 2 張單！"
    elif i > 0.8 and g > 0.6 and h > 0.02:
        return "📈 【強勢】主力拉升中，持股續抱！"
    elif g < 0.25 and h < 0.015 and i > 0.75:
        return "🟢 【買入/潛伏】完美地基，首單 1 張進場。"
    elif g < 0.6 and h < 0.025 and i > 0.5:
        return "🟡 【持股/監控】安靜累積，耐心等待訊號。"
    elif i <= 0.15 and h > 0.02:
        return "⚠️ 【警戒】高檔遇阻，供應湧現！"
    elif i < 0.3 and h > 0.03:
        return "🔴 【撤離/止損】結構崩塌，全數出清！"
    else:
        return "⚪ 【觀望】多空拉鋸，結構調整中"

def run_monitor():
    file_name = '台股-4533協易機-價量分析.csv'
    try:
        df = pd.read_csv(file_name, encoding='utf-8-sig', na_values=['#DIV/0!', '#N/A', '', ' '])
        
        # 1. 抓取關鍵欄位 (修正關鍵字，以符合你 CSV 的表頭)
        col_close = find_column(df, '收盤價')
        col_g = find_column(df, '努力') 
        col_h = find_column(df, '價格') # ★ 請確認你的 CSV 表頭是叫「價差」還是「價格」
        col_i = find_column(df, '意圖') # ★ 修正：從 '位置' 改成 '意圖'
        
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
        
        g_val = clean_value(latest_data.get(col_g)) if col_g else 0.0
        h_val = clean_value(latest_data.get(col_h)) if col_h else 0.0
        i_val = clean_value(latest_data.get(col_i)) if col_i else 0.0
        
        # ★★★ 關鍵除蟲手術：把百分比數字轉換回小數 ★★★
        # 如果抓到的數字大於 1，或者它本來在 Excel 裡就是百分比顯示的，我們就除以 100
        h_val = h_val / 100 
        i_val = i_val / 100
        
        # 4. 把數值丟進我們的大腦計算狀態
        calculated_status = get_vsa_status(g_val, h_val, i_val)

        # 5. 組裝 LINE 推播報告
        report = (
            f"\n--- 🐊 詩織機器人 盤後診斷報告 ({date}) ---\n"
            f"標的：4533 協易機\n"
            f"今日收盤：{close_price} 元\n"
            f"G(努力)：{g_val:.2f}x\n"
            f"H(價格)：{h_val:.3f}\n"
            f"I(意圖)：{i_val:.2f}\n"
            f"大鱷狀態：{calculated_status}\n"
        )

        # 加上原有的突破與止損提醒
        if close_price <= 30.0:
            report += "\n🚨 注意：已跌破 30.0 元止損位！"
        elif close_price >= 33.8:
            report += "\n🚀 突破：已站回 33.8 元關鍵地基！"
        else:
            report += "\n☕ 觀察：目前在地基區間內震盪，繼續喝紅茶。"

        print(report)
        send_line_message(report)

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        sys.exit(1)

if __name__ == "__main__":
    run_monitor()
