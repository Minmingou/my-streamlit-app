import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

st.title("주가 데이터 분석 웹앱")

# 1. 티커 입력받기
ticker = st.text_input("티커 입력", "TSLA")  # 기본값 TSLA

# 2. 기간 선택 슬라이더 (1 ~ 12개월)
months = st.slider("데이터 기간(개월) 선택", 1, 12, 6)  # 기본 6개월

# 3. yfinance에서 데이터 불러오기
if ticker:
    stock = yf.Ticker(ticker)
    df = stock.history(period=f"{months}mo")
    df = df.dropna()

    # 4. 이동평균선 계산
    df['MA10'] = df['Close'].rolling(window=10, min_periods=1).mean()
    df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
    df['MA60'] = df['Close'].rolling(window=60, min_periods=1).mean()

    # 5. 볼린저 밴드 계산
    df['BB_std'] = df['Close'].rolling(window=20, min_periods=1).std()
    df['BB_upper'] = df['MA20'] + 2 * df['BB_std']
    df['BB_lower'] = df['MA20'] - 2 * df['BB_std']

    # 6. RSI 계산
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss
    df['RSI14'] = 100 - (100 / (1 + rs))

    # 7. OBV 계산
    df['Direction'] = 0
    df.loc[df['Close'] > df['Close'].shift(1), 'Direction'] = 1
    df.loc[df['Close'] < df['Close'].shift(1), 'Direction'] = -1
    df['Volume_signed'] = df['Volume'] * df['Direction']
    df['OBV'] = df['Volume_signed'].cumsum()

    # 8. PER, EPS 가져오기
    info = stock.info
    per = info.get('trailingPE', 'N/A')
    eps = info.get('trailingEps', 'N/A')

    # 9. 차트 그리기
    plt.figure(figsize=(16, 14))

    # 주가 + 이동평균 + 볼린저밴드
    plt.subplot(3, 1, 1)
    plt.plot(df['Close'], label='Close Price', linewidth=1.5)
    plt.plot(df['MA10'], label='MA10', linestyle='--')
    plt.plot(df['MA20'], label='MA20', linestyle='--')
    plt.plot(df['MA60'], label='MA60', linestyle='--')
    plt.plot(df['BB_upper'], label='Bollinger Upper', linestyle='--', color='orange')
    plt.plot(df['BB_lower'], label='Bollinger Lower', linestyle='--', color='orange')
    plt.fill_between(df.index, df['BB_lower'], df['BB_upper'], color='orange', alpha=0.1)
    plt.title(f"{ticker} Price with MA & Bollinger Bands (PER: {per}, EPS: {eps})")
    plt.legend()
    plt.grid(True)

    # RSI
    plt.subplot(3, 1, 2)
    plt.plot(df['RSI14'], label='RSI (14)', color='purple')
    plt.axhline(70, color='red', linestyle='--', alpha=0.5)
    plt.axhline(30, color='blue', linestyle='--', alpha=0.5)
    plt.title("RSI (14-day)")
    plt.legend()
    plt.grid(True)

    # OBV
    plt.subplot(3, 1, 3)
    plt.plot(df['OBV'], label='On-Balance Volume (OBV)', color='green')
    plt.title("OBV")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    # 10. 스트림릿에 그래프 보여주기
    st.pyplot(plt)

else:
    st.write("티커를 입력해주세요.")
