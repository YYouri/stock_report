import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import yfinance as yf

# --- 1. 저장 폴더 & 파일 ---
os.makedirs('docs', exist_ok=True)
today = datetime.now().strftime('%Y-%m-%d')
report_file = f'docs/daily_report_{today}.md'

# --- 2. 파일 열기 ---
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(f"# 📅 {today} Daily Report\n\n")

    # --- 3. 경제 뉴스 수집 ---
    f.write("## 📰 경제 뉴스\n\n")
    news_url = "https://m.etnews.com/news/economy_list.html"
    res = requests.get(news_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    topnews_section = soup.select_one("section.textthumb")
    most_viewed = topnews_section.select('ul li strong a')[:5]

    for i, article in enumerate(most_viewed, 1):
        title = article.text.strip()
        link = "https://m.etnews.com" + article['href']
        f.write(f"{i}. [{title}]({link})\n")
    f.write("\n")

    # --- 4. 주식 리포트 수집 ---
    f.write("## 📈 주식 리포트\n\n")
    stocks = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    for symbol in stocks:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        f.write(f"### {symbol}\n")
        f.write("| 날짜 | 시가 | 고가 | 저가 | 종가 | 거래량 |\n")
        f.write("|------|------|------|------|------|------|\n")
        for date, row in hist.iterrows():
            f.write(f"| {date.date()} | {row['Open']:.2f} | {row['High']:.2f} | {row['Low']:.2f} | {row['Close']:.2f} | {int(row['Volume'])} |\n")
        f.write("\n")

print(f"✅ Daily report 생성 완료: {report_file}")

