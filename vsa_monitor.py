import os
import sys
import requests
import yfinance as yf
import pandas as pd

def send_line_message(message):
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('LINE_USER_ID')
    if not token or not user_id: 
        print("未設定 LINE Token 或 User ID")
        return
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    data = {'to': user_id, 'messages': [{'type': 'text', 'text': message}]}
    requests.post(url, headers=headers, json=data)

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

def analyze_stock(stock_id, stock_name, stop_loss, buy_point):
    """自動抓取並分析單檔股票"""
    try:
        # 1. 透過 Yahoo Finance 抓取過去 60 天的資料 (確保能算 50 日均量)
        ticker = yf.Ticker(stock_id)
        hist = ticker.history(period="60d")
        
        if hist.empty or len(hist) < 50:
            return f"❌ {stock_name} ({stock_id}): 無法取得足夠資料"

        # 2. 取得今天與昨天的資料
        today_data = hist.iloc[-1]
        yesterday_data = hist.iloc[-2]
        date_str = today_data.name.strftime('%Y/%m/%d')

        # 3. 提取原始數值
        close = today_data['Close']
        high = today_data['High']
        low = today_data['Low']
        vol_today = today_data['Volume']
        prev_close = yesterday_data['Close']
        
        # 4. Python 自行計算 G, H, I
        vol_50ma = hist['Volume'].rolling(window=50).mean().iloc[-1]
        
        g_val = vol_today / vol_50ma if vol_50ma > 0 else 0
        h_val = (high - low) / prev_close if prev_close > 0 else 0
        i_val = (close - low) / (high - low) if high != low else 0.5

        # 5. 大腦判定狀態
        status = get_vsa_status(g_val, h_val, i_val)

        # 6. 組裝報告
        report = (
            f"標的：{stock_name} ({stock_id.split('.')[0]})\n"
            f"今日收盤：{close:.2f} 元\n"
            f"G(努力)：{g_val:.2f}x\n"
            f"H(價差)：{h_val:.3f} ({h_val*100:.1f}%)\n"
            f"I(位置)：{i_val:.2f}\n"
            f"大鱷狀態：{status}\n"
        )

        # 專屬防線提醒
        if close <= stop_loss:
            report += f"🚨 注意：已跌破 {stop_loss} 元止損位！\n"
        elif close >= buy_point:
            report += f"🚀 突破：已站上 {buy_point} 元關鍵防線！\n"
        else:
            report += "☕ 觀察：安全區間內，繼續喝紅茶。\n"

        return report

    except Exception as e:
        return f"❌ 處理 {stock_name} 時發生錯誤: {e}"

def run_monitor():
    print("啟動自動化 VSA 掃描...")
    
    # 建立你想監控的清單 (台股代號後加上 .TW 代表上市，.TWO 代表上櫃)
    # 協易機是上櫃(TWO)，神達是上市(TW)
    watchlist = [
        {"id": "4533.TWO", "name": "協易機", "stop": 30.0, "buy": 33.8},
        {"id": "3706.TW", "name": "神達", "stop": 81.1, "buy": 82.3}
    ]

    final_report = f"\n--- 🐊 詩織機器人 盤後自動診斷 ---\n"
    
    for stock in watchlist:
        result = analyze_stock(stock["id"], stock["name"], stock["stop"], stock["buy"])
        final_report += f"\n{result}"
        final_report += "-" * 20

    print(final_report)
    send_line_message(final_report)

if __name__ == "__main__":
    run_monitor()
