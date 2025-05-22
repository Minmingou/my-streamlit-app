import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="주가 데이터 분석 웹앱", page_icon="📈")

FINNHUB_API_KEY = st.secrets["finnhub_api_key"]

lang_dict = {
    "한국어": {
        "title": "📊 실시간 주식 분석 웹앱",
        "ticker_input": "🔎 종목 티커 또는 기업명 입력",
        "months_range": "📆 데이터 기간(개월)",
        "show_chart": "📈 차트 표시 여부",
        "show_table": "📋 시장 데이터 요약",
        "show_finance": "💹 재무 정보 보기",
        "input_placeholder": "예: TSLA 또는 Tesla",
        "enter_ticker": "티커 또는 기업명을 입력해주세요.",
        "per": "PER",
        "eps": "EPS",
        "pb": "PBR",
        "op_margin": "영업이익률",
        "total_revenue": "총매출",
        "total_assets": "총자산",
        "financial_summary": "📊 재무 지표",
        "news_title": "📰 실시간 뉴스",
        "table_title": "📋 최근 10일 시장 데이터",
        "news_no_summary": "(요약 없음)",
        "current_price": "💰 실시간 현재가",
        # 최근 10일 시장 데이터 컬럼명
        "open": "시가",
        "close": "종가",
        "high": "고가",
        "low": "저가",
        "volume": "거래량",
        "volume_value": "거래대금",
        "price_change": "변동폭",
        "price_change_pct": "변동률(%)",
        "rsi": "RSI(14)"
    },
    "English": {
        "title": "📊 Stock Analysis App",
        "ticker_input": "🔎 Enter Stock Ticker or Company Name",
        "months_range": "📆 Data Period (months)",
        "show_chart": "📈 Show Chart",
        "show_table": "📋 Market Data Summary",
        "show_finance": "💹 Show Financial Info",
        "input_placeholder": "e.g. TSLA or Tesla",
        "enter_ticker": "Please enter a ticker or company name.",
        "per": "PER",
        "eps": "EPS",
        "pb": "PBR",
        "op_margin": "Operating Margin",
        "total_revenue": "Total Revenue",
        "total_assets": "Total Assets",
        "financial_summary": "📊 Financial Summary",
        "news_title": "📰 Real-Time News",
        "table_title": "📋 Latest 10 Days Market Data",
        "news_no_summary": "(No summary)",
        "current_price": "💰 Current Price",
        # 최근 10일 시장 데이터 컬럼명
        "open": "Open",
        "close": "Close",
        "high": "High",
        "low": "Low",
        "volume": "Volume",
        "volume_value": "Value",
        "price_change": "Price Change",
        "price_change_pct": "Change (%)",
        "rsi": "RSI(14)"
    },
    "简体中文": {
        "title": "📊 实时股票分析应用",
        "ticker_input": "🔎 输入股票代码或公司名称",
        "months_range": "📆 数据周期（月）",
        "show_chart": "📈 显示图表",
        "show_table": "📋 市场数据摘要",
        "show_finance": "💹 显示财务信息",
        "input_placeholder": "例如: TSLA 或 Tesla",
        "enter_ticker": "请输入股票代码或公司名称。",
        "per": "市盈率",
        "eps": "每股收益",
        "pb": "市净率",
        "op_margin": "营业利润率",
        "total_revenue": "总收入",
        "total_assets": "总资产",
        "financial_summary": "📊 财务摘要",
        "news_title": "📰 实时新闻",
        "table_title": "📋 最近10天市场数据",
        "news_no_summary": "(无摘要)",
        "current_price": "💰 实时价格",
        # 최근 10일 시장 데이터 컬럼명
        "open": "开盘价",
        "close": "收盘价",
        "high": "最高价",
        "low": "最低价",
        "volume": "成交量",
        "volume_value": "成交额",
        "price_change": "价格变化",
        "price_change_pct": "变化率(%)",
        "rsi": "RSI(14)"
    },
    "日本語": {
        "title": "📊 リアルタイム株式分析アプリ",
        "ticker_input": "🔎 銘柄ティッカーまたは会社名を入力",
        "months_range": "📆 データ期間（月）",
        "show_chart": "📈 チャート表示",
        "show_table": "📋 市場データ概要",
        "show_finance": "💹 財務情報表示",
        "input_placeholder": "例: TSLA または Tesla",
        "enter_ticker": "ティッカーまたは会社名を入力してください。",
        "per": "PER",
        "eps": "EPS",
        "pb": "PBR",
        "op_margin": "営業利益率",
        "total_revenue": "総収益",
        "total_assets": "総資産",
        "financial_summary": "📊 財務概要",
        "news_title": "📰 リアルタイムニュース",
        "table_title": "📋 最新10日間の市場データ",
        "news_no_summary": "(要約なし)",
        "current_price": "💰 リアルタイム価格",
        # 최근 10일 시장 데이터 컬럼명
        "open": "始値",
        "close": "終値",
        "high": "高値",
        "low": "安値",
        "volume": "出来高",
        "volume_value": "出来高金額",
        "price_change": "変動幅",
        "price_change_pct": "変動率(%)",
        "rsi": "RSI(14)"
    }
}

lang = st.sidebar.selectbox("🌍 Language / 언어 / 语言 / 言語", list(lang_dict.keys()))
T = lang_dict[lang]

st.title(T["title"])

user_input = st.sidebar.text_input(T["ticker_input"], "TSLA", placeholder=T["input_placeholder"])
months = st.sidebar.slider(T["months_range"], 1, 12, 6)
show_chart = st.sidebar.checkbox(T["show_chart"], True)
show_table = st.sidebar.checkbox(T["show_table"], True)
show_finance = st.sidebar.checkbox(T["show_finance"], False)

def find_ticker_by_name(name):
    """
    간단 매핑 - yfinance에 공식 API가 없어 임의로 회사명-티커 딕셔너리 사용.
    필요하면 여기에 기업명-티커 추가.
    """
    candidates = {
        "TSLA": "Tesla, Inc.",
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "O": "Realty Income Corporation",
        "GOOGL": "Alphabet Inc.",
        "AMZN": "Amazon.com, Inc."
    }
    name = name.lower()
    for ticker, company in candidates.items():
        if name in ticker.lower() or name in company.lower():
            return ticker
    return None

if user_input:
    ticker = user_input.upper()
    stock = yf.Ticker(ticker)
    info = stock.info

    if not info or 'shortName' not in info:
        found_ticker = find_ticker_by_name(user_input)
        if found_ticker:
            ticker = found_ticker
            stock = yf.Ticker(ticker)
            info = stock.info
        else:
            st.warning(T["enter_ticker"])
            st.stop()

    realtime_price = info.get("regularMarketPrice", None)
    if realtime_price:
        st.markdown(f"### {ticker} - {info.get('shortName', '')}")
        st.markdown(f"**{T['current_price']}:** ${realtime_price:.2f}")
    else:
        st.markdown(f"### {ticker} - {info.get('shortName', '')}")
        st.markdown("실시간 가격 정보를 불러올 수 없습니다.")

    df = stock.history(period=f"{months}mo").dropna()

    df['MA10'] = df['Close'].rolling(10).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA60'] = df['Close'].rolling(60).mean()

    df['BB_std'] = df['Close'].rolling(20).std()
    df['BB_upper'] = df['MA20'] + 2 * df['BB_std']
    df['BB_lower'] = df['MA20'] - 2 * df['BB_std']

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['RSI14'] = 100 - (100 / (1 + rs))

    df['Direction'] = 0
    df.loc[df['Close'] > df['Close'].shift(1), 'Direction'] = 1
    df.loc[df['Close'] < df['Close'].shift(1), 'Direction'] = -1
    df['Volume_signed'] = df['Volume'] * df['Direction']
    df['OBV'] = df['Volume_signed'].cumsum()

    if show_chart:
        plt.figure(figsize=(16, 14))

        plt.subplot(3, 1, 1)
        plt.plot(df['Close'], label='Close Price')
        plt.plot(df['MA10'], label='MA10', linestyle='--')
        plt.plot(df['MA20'], label='MA20', linestyle='--')
        plt.plot(df['MA60'], label='MA60', linestyle='--')
        plt.plot(df['BB_upper'], label='Bollinger Upper', linestyle='--', color='orange')
        plt.plot(df['BB_lower'], label='Bollinger Lower', linestyle='--', color='orange')
        plt.title(f"{ticker} Price and Moving Averages")
        plt.legend()

        plt.subplot(3, 1, 2)
        plt.plot(df['RSI14'], label='RSI (14)')
        plt.axhline(70, color='red', linestyle='--')
        plt.axhline(30, color='green', linestyle='--')
        plt.title("Relative Strength Index")
        plt.legend()

        plt.subplot(3, 1, 3)
        plt.plot(df['OBV'], label='On-Balance Volume')
        plt.title("On-Balance Volume")
        plt.legend()

        plt.tight_layout()
        st.pyplot(plt)

    if show_table:
        df.index = df.index.tz_localize(None)
        last_10 = df.tail(10).copy()
        
        # 컬럼명 언어별 변환
        rename_cols = {
            'Open': T['open'],
            'High': T['high'],
            'Low': T['low'],
            'Close': T['close'],
            'Volume': T['volume']
        }
        last_10 = last_10.rename(columns=rename_cols)
        last_10['Date'] = last_10.index.date.astype(str)
        #last_10['Date'] = last_10.index.strftime('%Y-%m-%d')
        last_10 = last_10[[T['open'], T['high'], T['low'], T['close'], T['volume']]]
        # 변동폭, 변동률(%) 추가
        last_10[T['price_change']] = last_10[T['close']].diff()
        last_10[T['price_change_pct']] = last_10[T['close']].pct_change() * 100
        last_10 = last_10.iloc[1:]
        st.subheader(T["table_title"])
        st.dataframe(last_10.style.format({
            T['price_change']: "{:.2f}",
            T['price_change_pct']: "{:.2f}%",
            T['open']: "{:.2f}",
            T['high']: "{:.2f}",
            T['low']: "{:.2f}",
            T['close']: "{:.2f}"
        }))
    if show_finance:
        st.subheader(T["financial_summary"])
        per = info.get("trailingPE", "N/A")
        eps = info.get("trailingEps", "N/A")
        pb = info.get("priceToBook", "N/A")
        op_margin = info.get("operatingMargins", "N/A")
        total_revenue = info.get("totalRevenue", "N/A")
        total_assets = info.get("totalAssets", "N/A")

        st.write(f"{T['per']}: {per}")
        st.write(f"{T['eps']}: {eps}")
        st.write(f"{T['pb']}: {pb}")
        st.write(f"{T['op_margin']}: {op_margin}")
        st.write(f"{T['total_revenue']}: {total_revenue}")
        st.write(f"{T['total_assets']}: {total_assets}")

    # Finnhub 실시간 뉴스
    if FINNHUB_API_KEY and ticker:
        st.subheader(T["news_title"])
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now() - pd.DateOffset(months=months)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            news_list = response.json()
            if len(news_list) == 0:
                st.write("No recent news found.")
            else:
                for news in news_list[:5]:
                    dt = datetime.fromtimestamp(news.get('datetime', 0))
                    st.markdown(f"[{news.get('headline', T['news_no_summary'])}]({news.get('url', '#')}) - {dt.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.write("뉴스를 불러올 수 없습니다.")
else:
    st.info(T["enter_ticker"])

    

