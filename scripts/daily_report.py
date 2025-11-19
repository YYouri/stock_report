import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import yaml

# --- 1. 설정 읽기 ---
with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

news_url = config["news"]["url"]
top_n = config["news"]["top_n"]
stocks = config["stocks"]["symbols"]
history_days = config["stocks"]["history_days"]

# --- 2. 저장 폴더 & 파일 ---
os.makedirs("docs", exist_ok=True)
today = datetime.now().strftime("%Y-%m-%d")
report_file = f"docs/daily_report_{today}.md"

# --- 3. Markdown 작성 ---
with open(report_file, "w", encoding="utf-8") as f:
    f.write(f"# 📅 {today} Daily Report\n\n")

    # --- 4. 뉴스 수집 ---
    f.write("## 📰 경제 뉴스\n\n")
    try:
        res = requests.get(news_url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        selector = "section.news_sec.top_news_sec.is_active ul li a div h3"
        articles = soup.select(selector)[:top_n]
        if not articles:
            f.write("뉴스 데이터를 불러오지 못했습니다.\n\n")
        for i, article in enumerate(articles, 1):
            title = article.text.strip()
            link = article.get("href")
            if not link.startswith("http"):
                link = "https://m.mk.co.kr" + link
            f.write(f"{i}. [{title}]({link})\n")
    except Exception as e:
        f.write(f"뉴스 수집 중 오류 발생: {e}\n\n")

    # --- 5. 주식 리포트 ---
    f.write("## 📈 주식 리포트\n\n")
    for symbol in stocks:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f"{history_days}d")
            if hist.empty:
                f.write(f"{symbol} 데이터 없음\n\n")
                continue
            f.write(f"### {symbol}\n")
            f.write("| 날짜 | 시가 | 고가 | 저가 | 종가 | 거래량 |\n")
            f.write("|------|------|------|------|------|------|\n")
            for date, row in hist.iterrows():
                f.write(f"| {date.date()} | {row['Open']:.2f} | {row['High']:.2f} | {row['Low']:.2f} | {row['Close']:.2f} | {int(row['Volume'])} |\n")
            f.write("\n")
        except Exception as e:
            f.write(f"{symbol} 데이터 수집 중 오류 발생: {e}\n\n")

print(f"✅ Daily report 생성 완료: {report_file}")
