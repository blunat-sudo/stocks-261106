import streamlit as st
from pykrx import stock
import datetime

# 페이지 기본 설정
st.set_page_config(page_title="내 주식 자산 계산기", layout="wide")

st.title("📈 주식 보유 자산 실시간 계산기")
st.caption("한국거래소(KRX) 데이터를 기반으로 최근 거래 가격을 조회합니다.")

# 사용자 입력 화면 구성 (2개 열로 분할)
col1, col2 = st.columns(2)

with col1:
    st.subheader("첫 번째 종목")
    code1 = st.text_input("종목코드 1 (6자리)", value="005930", key="c1")
    qty1 = st.number_input("보유 수량 1 (주)", min_value=0, value=10, key="q1")

with col2:
    st.subheader("두 번째 종목")
    code2 = st.text_input("종목코드 2 (6자리)", value="000660", key="c2")
    qty2 = st.number_input("보유 수량 2 (주)", min_value=0, value=5, key="q2")

st.markdown("---")

# 최근 거래일의 종가를 가져오는 함수
def get_current_price(ticker_code):
    try:
        # 오늘 날짜 확인
        today = datetime.date.today().strftime("%Y%m%d")
        # 종목 이름 가져오기
        name = stock.get_market_ticker_name(ticker_code)
        
        # 최근 시세 가져오기
        df = stock.get_market_ohlcv_by_date(today, today, ticker_code)
        
        # 장 시작 전이거나 휴일이라 오늘 데이터가 없으면 최근 7일간의 최신 종가 조회
        if df.empty:
            start_date = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y%m%d")
            df = stock.get_market_ohlcv_by_date(start_date, today, ticker_code)
            
        latest_price = df['종가'].iloc[-1]
        return name, int(latest_price)
    except Exception as e:
        return None, 0

# 계산 버튼 생성
if st.button("🔄 실시간 시세 및 평가금액 계산하기", use_container_width=True):
    with st.spinner("한국거래소에서 주가 정보를 불러오는 중..."):
        name1, price1 = get_current_price(code1)
        name2, price2 = get_current_price(code2)

    if price1 == 0 or price2 == 0:
        st.error("종목코드를 확인해 주세요. (예: 삼성전자 005930, SK하이닉스 000660)")
    else:
        total1 = price1 * qty1
        total2 = price2 * qty2
        grand_total = total1 + total2

        # 결과 출력
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.metric(label=f"{name1} ({code1})", value=f"{price1:,.0f} 원", delta=f"보유금액: {total1:,.0f} 원")
            
        with res_col2:
            st.metric(label=f"{name2} ({code2})", value=f"{price2:,.0f} 원", delta=f"보유금액: {total2:,.0f} 원")

        st.markdown("---")
        st.success(f"### 💰 총 보유 자산 합계: **{grand_total:,.0f} 원**")