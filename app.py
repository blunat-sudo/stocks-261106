import streamlit as st
from pykrx import stock
import datetime
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="내 주식 포트폴리오 자산 계산기", layout="wide")

st.title("📈 주식 보유 자산 및 5일 변동 추이 계산기")
st.caption("한국거래소(KRX) 데이터를 기반으로 실시간(지연) 시세와 과거 5일간의 자산 변동을 추적합니다.")

# 1. 사용자 입력 화면 구성 (기본값 고정 및 수정 가능)
col1, col2 = st.columns(2)

with col1:
    st.subheader("첫 번째 종목: 삼성전자")
    code1 = st.text_input("종목코드 1", value="005930", key="c1", disabled=True)
    qty1 = st.number_input("보유 수량 1 (주)", min_value=0, value=1722, key="q1")

with col2:
    st.subheader("두 번째 종목: 해성에어로보틱스")
    # 해성에어로보틱스 종목코드 예시 (정확한 코드로 수정 가능)
    code2 = st.text_input("종목코드 2", value="381970", key="c2") 
    qty2 = st.number_input("보유 수량 2 (주)", min_value=0, value=200, key="q2")

st.markdown("---")

# 2. 새로고침 버튼 생성
if st.button("🔄 새로고침 및 자산 재계산하기", use_container_width=True):
    st.rerun()

# 3. 데이터 조회 및 계산 함수 (과거 5일 포함)
def get_stock_data(ticker_code, qty):
    try:
        today = datetime.date.today()
        # 영업일 기준 넉넉하게 15일 전부터 오늘까지 조회하여 최근 5개 거래일 추출
        start_date = (today - datetime.timedelta(days=15)).strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")
        
        name = stock.get_market_ticker_name(ticker_code)
        df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker_code)
        
        if df.empty:
            return name, 0, pd.DataFrame()
            
        # 최근 5일 데이터만 추출
        df_recent = df.tail(5).copy()
        current_price = int(df_recent['종가'].iloc[-1])
        
        return name, current_price, df_recent
    except Exception as e:
        return "조회 실패", 0, pd.DataFrame()

with st.spinner("한국거래소에서 주가 및 과거 5일 데이터를 불러오는 중..."):
    name1, price1, df1 = get_stock_data(code1, qty1)
    name2, price2, df2 = get_stock_data(code2, qty2)

if price1 == 0 or price2 == 0:
    st.error("종목코드를 확인해 주세요. (해성에어로보틱스 등 코드가 정확한지 확인 필요)")
else:
    # 현재 보유금액 및 총합계 산출
    total1 = price1 * qty1
    total2 = price2 * qty2
    grand_total = total1 + total2

    # 화면 분할 배치 (왼쪽: 현재 요약 및 합계 / 오른쪽: 과거 5일 변동 목록)
    layout_col1, layout_col2 = st.columns([1, 1.2])

    with layout_col1:
        st.subheader("📊 현재 자산 평가 요약")
        st.metric(label=f"{name1} ({qty1}주)", value=f"{price1:,.0f} 원", delta=f"평가금액: {total1:,.0f} 원")
        st.metric(label=f"{name2} ({qty2}주)", value=f"{price2:,.0f} 원", delta=f"평가금액: {total2:,.0f} 원")
        
        st.markdown("---")
        st.success(f"### 💰 총 보유 자산 합계\n# **{grand_total:,.0f} 원**")

    with layout_col2:
        st.subheader("📅 과거 5일간 날짜별 자산 변동 목록")
        
        # 날짜별 합산 데이터프레임 생성
        try:
            # 두 종목의 날짜 인덱스 교집합 또는 합집합 활용을 위해 날짜 기준 정렬
            combined_df = pd.DataFrame(index=df1.index)
            combined_df[f'{name1} 종가'] = df1['종가']
            combined_df[f'{name2} 종가'] = df2['종가']
            combined_df = combined_df.dropna() # 데이터가 모두 존재하는 날짜만
            
            # 날짜별 총 자산 합계 계산
            combined_df['종목1 평가액'] = combined_df[f'{name1} 종가'] * qty1
            combined_df['종목2 평가액'] = combined_df[f'{name2} 종가'] * qty2
            combined_df['총 자산 합계'] = combined_df['종목1 평가액'] + combined_df['종목2 평가액']
            
            # 보기 편하게 날짜 형식 변환 및 컬럼 정리
            display_df = pd.DataFrame({
                '날짜': combined_df.index.strftime('%Y-%m-%d'),
                f'{name1} 주가': combined_df[f'{name1} 종가'].map('{:,.0f}원'.format),
                f'{name2} 주가': combined_df[f'{name2} 종가'].map('{:,.0f}원'.format),
                '날짜별 총 자산 합계': combined_df['총 자산 합계'].map('{:,.0f}원'.format)
            })
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        except Exception as ex:
            st.warning("과거 5일 데이터를 동기화하는 중 일부 차이가 발생했습니다. 주말이나 휴일일 경우 최근 영업일 기준으로 표시됩니다.")