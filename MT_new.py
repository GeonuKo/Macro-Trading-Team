import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import os

# 0. 페이지 설정
st.set_page_config(
    page_title="하나증권 외화운용실 플랫폼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 메뉴 설정
with st.sidebar:
    st.title("목록")
    menu = st.radio(
        "이동할 페이지를 클릭하세요",
        ["메인 대시보드", "FOMC", "ECB", "BOK", "경제지표 캘린더"], 
        index=0
    )

# 1. 데이터 가져오기 함수 (진단 모드 포함)
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = 'market.db'  # 위와 동일하게 파일명만 입력
st.write("현재 연결된 DB 경로:", os.path.abspath(db_path))

def get_data():
    import os
    # 파일이 실제로 존재하는지 먼저 확인
    if not os.path.exists(db_path):
        return pd.DataFrame() 
    
    try:
        with sqlite3.connect(db_path) as conn:
            # feeder가 만든 'rates' 테이블을 읽어옴
            df = pd.read_sql("SELECT * FROM rates", conn)
            return df
    except Exception as e:
        # 에러가 나면 화면에 표시해서 원인을 알 수 있게 함
        st.error(f"데이터 로딩 에러: {e}")
        return pd.DataFrame()

# --- 페이지 함수 정의 ---
def main_dashboard():
    st.set_page_config(page_title="하나증권 외화운용실", layout="wide")
    st.title("하나증권 외화운용실 공유 플랫폼")
    st.write(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # --- [1단계: 실시간 금리 요약 (DB 연동)] ---
    st.subheader("📊 Global Benchmark Yields (Real-time)")
    
    df = get_data()

    if df.empty:
        st.error("데이터 보관함에서 자료를 찾을 수 없습니다.")
        st.info(f"현재 프로그램이 찾고 있는 경로: {os.path.abspath(db_path)}")
    else:
        # 데이터가 있다면 화면에 출력 (이 코드가 있는지 확인!)
        st.dataframe(df)

    st.divider()

    # --- [2단계: 경제지표 캘린더 (수정사항 반영)] ---
    st.subheader("🗓️ Today's Economic Calendar")
    
    # 요청하신 7가지 항목을 포함한 샘플 데이터
    calendar_data = {
        "발표시간": ["16:00", "21:30", "21:30", "23:00", "23:00"],
        "국가": ["DE", "US", "US", "US", "US"],
        "지표명": [
            "독일 소비자물가지수(CPI) (전월비)", 
            "미국 비농업 고용지수", 
            "미국 실업률", 
            "ISM 비제조업 PMI",
            "미국 공장수주"
        ],
        "중요도": ["⭐⭐", "⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐", "⚠️"],
        "실제치": ["0.3%", "-", "-", "-", "-"], # 발표 전은 "-"
        "예측치": ["0.2%", "185K", "3.9%", "51.4", "0.5%"],
        "이전치": ["0.1%", "203K", "3.8%", "52.6", "-0.8%"]
    }

    df_calendar = pd.DataFrame(calendar_data)

    # 표 형태로 출력 (지표명, 발표시간, 국가, 중요도, 실제치, 예측치, 이전치 순서)
    st.table(df_calendar[["지표명", "발표시간", "국가", "중요도", "실제치", "예측치", "이전치"]])

    st.info("💡 실시간 금리는 1분마다 자동으로 업데이트됩니다.")



def fomc_page():
    # 헤더 섹션
    st.title("🇺🇸 FOMC Review (2026.04)")
    st.caption("회의 일자: 2026년 4월 29-30일 | 작성일: 2026년 4월 30일")

    # 상단 핵심 지표 (Metrics)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("금리 결정", "3.50~3.75%", "동결 (Unchanged)")
    with m_col2:
        st.metric("소수 의견 (Dissents)", "4명", "Hawkish Surprise", delta_color="inverse")
    with m_col3:
        st.metric("차기 의장", "Kevin Warsh", "5월 취임 예정")
    with m_col4:
        st.metric("파월 행보", "이사직 잔류", "연준 독립성 수호")

    st.divider()

    # 1. 주요 결정 사항 및 파월 기자회견 핵심
    st.subheader("1. 주요 포인트: 매파적 동결 (Hawkish Hold)")
    c1, c2 = st.columns(2)
    with c1:
        st.info("### 📌 핵심 하이라이트")
        st.markdown("""
        - **가이던스 충돌:** '완화 편향(Easing Bias)' 문구는 유지되었으나, 매파적 소수 의견(3명)이 강력 제기됨.
        - **파월의 결단:** 의장직 종료 후에도 이사(Governor)로 잔류. "연준 독립성 수호" 목적 명시.
        - **인플레이션 인식:** "인플레이션이 말을 듣지 않는다(Misbehaving)"며 고착화 경계심 노골적 표현.
        """)
    with c2:
        st.success("### ⚖️ 위원회 내 분열 (Dissents)")
        st.markdown("""
        - **매파적 반대 (3명):** Hammack, Kashkari, Logan (완화 가이던스 삭제 및 인상 가능성 열어둘 것 요구)
        - **비둘기파적 반대 (1명):** Miran (금리 인하 주장)
        - **결론:** 위원회의 '중심(Center)'이 중립으로 이동 중이며, 데이터에 따라 향후 **추가 금리 인상** 논의 가능성 부각.
        """)

    # 2. 주요 IB별 심층 분석
    st.subheader("2. 주요 IB별 심층 분석: Policy Path & View")
    
    # JPM & MS 상세 분석 (Column 1)
    col_ib1, col_ib2 = st.columns(2)
    
    with col_ib1:
        with st.container(border=True):
            st.markdown("#### JP Morgan: '분열된 위원회와 파월의 결단'")
            st.markdown("""
            - **금리 전망:** 2026년 동결 유지, 차기 행보는 **내년 후반 금리 인상(Firming)** 예상.
            - **파월의 행보:** 이사 잔류 결정은 연준의 독립성을 수호하려는 '체크 앤 밸런스' 의도. 이는 정책이 정치적 압력보다 **데이터 의존적(Data-dependent)**으로 유지되는 데 기여할 것.
            - **가이던스 해석:** '추가 조정' 문구가 인하를 시사한다는 논란이 있으나, 파월은 차기 의장(Warsh)에게 정책 결정의 자율성을 주기 위해 가이던스 변경을 차기 회의로 미룬 것으로 분석.
            - **인플레 경계:** "노동시장은 안정적이나 인플레이션은 말을 듣지 않는다(Misbehaving)"는 파월의 발언에 주목.
            """)

        with st.container(border=True):
            st.markdown("#### Morgan Stanley: '중립으로의 이동'")
            st.markdown("""
            - **금리 전망:** **2026년 연말까지 Hold**. 이후 2027년 1월과 3월에 각 25bp 인하 예상.
            - **핵심 논리:** 위원회의 중심이 완화 편향에서 **중립(Neutral)**으로 이동 중. 인플레이션 둔화는 '추측'이 아닌 '증거'가 필요하며, 현재 경제는 이를 기다릴 만큼 충분히 강력함.
            - **가이던스 변화:** 가이던스의 변화는 데이터 신호에 선행하기보다 후행할 것(Lag).
            """)

    # BofA & SG 상세 분석 (Column 2)
    with col_ib2:
        with st.container(border=True):
            st.markdown("#### BofA: '매파적인 백조의 노래(Hawkish Swan Song)'")
            st.markdown("""
            - **시장 영향:** 3명의 매파적 소수 의견(Dissent)이 가장 큰 서프라이즈. 채권 시장은 이를 즉각 반영하며 **커브 플래트닝(2Y +9bp)** 발생.
            - **자산군 전망:** 
                - **채권:** 시장이 인플레 리스크는 잘 반영하고 있으나, 성장 하방 리스크는 과소평가 중.
                - **FX:** 매파적 소수 의견이 달러 강세를 지지했으나, 중장기적으로는 달러화의 완만한 약세 전망 유지(ECB/BoE의 인상 가능성 대비).
            - **B/S 정책:** 5월 중순부터 QT 속도 조절 예상 ($25b/m → $20b/m).
            """)

        with st.container(border=True):
            st.markdown("#### Societe Generale: '인상 가능성의 대두'")
            st.markdown("""
            - **금리 전망:** 2026년 내 인하 없음.
            - **리스크 시나리오:** 올해 중반까지 코어 인플레 수치에 진전이 없다면, FOMC 내부 논의는 **'인상(Hike) 가능성'**을 공식적으로 검토하기 시작할 것. 
            - **관전 포인트:** 현재 완화 편향을 제거하려는 위원들의 수가 상당하다는 점에 주목해야 함.
            """)
        
def ecb_page():
    # 헤더 섹션
    st.title("🇪🇺 ECB Preview")
    st.caption("작성일: 2026년 4월 30일 | 출처: 주요 IB 보고서 및 ECB Press Release")
    
    # 상단 핵심 요약 (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("현재 금리", "2.00%", help="Deposit Facility 기준")
    with col2:
        st.metric("시장 동결 확률", "73%", delta="Polymarket 기준")
    with col3:
        st.metric("HICP (3월 YoY)", "2.5%", delta="0.6%p 상향", delta_color="inverse")
    with col4:
        st.metric("Brent 유가", "$105", delta="이란-미국 전쟁 영향")

    st.divider()

    # 1. 매크로 배경 및 시나리오 분석
    st.subheader("1. 매크로 배경 및 시나리오")
    m_col1, m_col2 = st.columns([1, 1])
    with m_col1:
        st.markdown("""
        **핵심 이슈: 이란-미국 전쟁 및 호르무즈 봉쇄**
        * **인플레 전망:** 2026년 HICP 전망치 2.6%로 상향 (에너지 주도).
        * **성장률 둔화:** GDP 전망 0.9%로 하향, 유로존의 높은 에너지 의존도 부각.
        * **안정 지표:** Core HICP(2.3%) 및 5Y5Y 인플레 스왑(2.14%)은 아직 관리 범위 내.
        """)
    with m_col2:
        macro_data = {
            "Indicator": ["HICP (3월)", "Core HICP", "GDP (2026F)", "Brent 유가"],
            "Value": ["2.5%", "2.3%", "+0.9%", "$105"]
        }
        st.table(pd.DataFrame(macro_data))

    # 2. IB 5사 핵심 뷰 (Table 형태)
    st.subheader("2. IB 5사 금리 및 정책 전망")
    ib_data = {
        "증권사": ["JP Morgan", "Goldman Sachs", "Morgan Stanley", "Citi", "Bank of America"],
        "금리 전망": ["6/7월 각 +25bp", "6월 +25bp 유력", "6/9월 각 +25bp", "경로 불확실", "동결 유지"],
        "스탠스": ["Extreme Hawkish", "Hawkish", "Hawkish", "Neutral", "Dovish/Cautious"],
        "핵심 뷰": [
            "에너지 2차 효과 선제 대응 필요, 최대 3회 인상 가능성",
            "Very adverse 시나리오 시 6월 +75bp 누적 인상",
            "Data-dependent 기조 유지하나 총 +50bp 인상 예상",
            "에너지 직접 효과만으론 부족, Brent $150 시나리오 시 검토",
            "스태그플레이션 경고, 추가 긴축은 정책 실수"
        ]
    }
    st.dataframe(pd.DataFrame(ib_data), use_container_width=True, hide_index=True)

    # 3. 핵심 관전포인트
    st.subheader("3. 핵심 관전포인트")
    with st.expander("① Lagarde 톤 및 포워드 가이던스", expanded=True):
        st.write("6월 인상(hike) 선제 시그널 여부가 EUR/USD 및 Bund 방향성 결정.")
    with st.expander("② 성장 vs 인플레 밸런스"):
        st.write("GDP 0.9% 약화에 대한 ECB의 인식 확인 필요. 스태그플레이션 우려 인정 여부가 관건.")

    st.info("**Bottom Line:** 4월 동결은 기정사실화. 관건은 6월 인상 시그널의 강도입니다. 성장 하방 리스크가 미국보다 크다는 점이 월가 뷰 분열의 핵심입니다.")

    # 4. 시각화 (간이 스펙트럼)
    st.subheader("4. 월가 정책 스펙트럼")
    st.progress(80, text="Hawkish (JPM, GS, MS) <---------- Neutral (Citi) ----------> Dovish (BofA)")

def bok_page():
    # 헤더 섹션
    st.title("🇰🇷 BOK & Korea Fixed Income Strategy")
    st.caption("작성일: 2026년 4월 30일 | 채권 Strategist: 박준우, CFA")

    # 1. 핵심 지표 (Metrics)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("BOK 기준금리", "3.50%", "7회 연속 동결")
    with m_col2:
        st.metric("3년물 금리 전망 (4Q)", "3.10%", "▼ 하향 재개")
    with m_col3:
        st.metric("2026 성장률(F)", "1.8%↓", "2월 전망비 -0.2%p", delta_color="inverse")
    with m_col4:
        st.metric("2026 물가(F)", "2%대 중후반↑", "상향 조정 시사")

    st.divider()

    # 2. 4월 금통위 리뷰: "선제적 인상보다 관망(Wait & See)"
    st.subheader("1. 4월 금통위 리뷰: 유가 충격에 대한 신중한 대응")
    
    col_rev1, col_rev2 = st.columns([3, 2])
    
    with col_rev1:
        st.markdown("""
        **주요 결정 및 통화정책방향문 변화**
        *   **만장일치 동결:** 작년 5월 이후 7회 연속 동결 유지.
        *   **가이던스 변경:** '성장세 회복 지원' 문구 삭제 → **'물가 및 성장 흐름 점검'**으로 대체.
        *   **공급 쇼크 원칙:** 유가 상승 등 공급 충격이 일시적일 경우 정책 대응 지양, 장기화되어 기대 인플레 불안 시에만 대응.
        *   **금융안정:** 환율 변동성은 확대되었으나, 가계대출 및 주택가격 상승 기대는 완화되었다고 평가.
        """)
    
    with col_rev2:
        with st.container(border=True):
            st.markdown("#### ⚖️ BOK의 고민: 스태그플레이션 리스크")
            st.warning("**성장 하방 + 물가 상방**")
            st.write("- 2022년 대비 수요가 약하고 부문간 격차가 커 성장 충격 우려가 큼.")
            st.write("- 중동 의존도가 높아 공급 충격의 인플레 영향은 과거보다 강할 가능성.")

    # 3. 기준금리 및 국채금리 전망
    st.subheader("2. 전망: 연내 동결 및 국채금리 하방 압력")
    
    tab_rate, tab_bond = st.tabs(["기준금리 전망", "국채금리 전망(Fixed Income)"])
    
    with tab_rate:
        st.markdown("#### **[기준금리] 2026년 연내 동결 전망**")
        st.markdown("""
        1.  **제한적인 2차 파급 효과:** 유가 고점 통과 시 기대 인플레이션의 추세적 상승 가능성 낮음.
        2.  **전망의 불확실성:** 아시아 국가는 성장/물가 충격이 동시에 커 선제적 대응이 물리적으로 어려움.
        3.  **긴축 전환의 허들:** 정책 시차(약 1년) 고려 시, 인플레 파도 이후 경제에 악영향을 미칠 리스크 존재.
        4.  **정책 연속성:** 신현송 차기 후보자(4/21 취임 예정) 역시 유가 충격에 대한 신중론 및 환율 우려 경계 입장.
        """)

    with tab_bond:
        st.markdown("#### **[국채금리] 물가 리스크 견딘 후 하락 재개**")
        st.info("시장 내 1~2회 금리 인상 우려가 완화되며 금리는 하향 안정화될 것")
        
        # 금리 경로 데이터프레임
        path_data = {
            "구분": ["4~5월 (단기)", "2분기 평균", "4분기 전망"],
            "3년물 국채금리": ["3.50%", "3.40%", "3.10%"],
            "비고": ["변동성 장세/반등 리스크", "물가 리스크 반영", "성장 리스크 부각 및 하락"]
        }
        st.table(pd.DataFrame(path_data))
        st.caption("*유가 충격이 '물가 상승'을 먼저 일으키고, '성장 둔화'를 나중에 일으키는 시차(Lag)에 주목")

def get_calendar_data():
    data = [
        # --- 2026년 4월 ---
        {"date": "2026-04-01", "time": "21:15", "country": "🇺🇸", "event": "ADP 비농업부문 고용 변화 (3월)", "imp": "★★★", "actual": "62K", "forecast": "41K", "previous": "66K"},
        {"date": "2026-04-01", "time": "21:30", "country": "🇺🇸", "event": "소매판매 (MoM) (2월)", "imp": "★★★", "actual": "0.60%", "forecast": "0.50%", "previous": "-0.10%"},
        {"date": "2026-04-01", "time": "21:30", "country": "🇺🇸", "event": "근원 소매판매 (MoM) (2월)", "imp": "★★★", "actual": "0.50%", "forecast": "0.30%", "previous": "0.00%"},
        {"date": "2026-04-01", "time": "22:45", "country": "🇺🇸", "event": "제조업 구매관리자지수 (3월)", "imp": "★★☆", "actual": "52.3", "forecast": "52.4", "previous": "51.6"},
        {"date": "2026-04-01", "time": "23:00", "country": "🇺🇸", "event": "ISM 제조업구매자지수 (3월)", "imp": "★★★", "actual": "52.7", "forecast": "52.3", "previous": "52.4"},
        {"date": "2026-04-01", "time": "23:30", "country": "🇺🇸", "event": "원유재고", "imp": "★★☆", "actual": "5.451M", "forecast": "1.800M", "previous": "6.926M"},

        {"date": "2026-04-02", "time": "08:00", "country": "🇰🇷", "event": "한국 소비자물가지수 (MoM) (3월)", "imp": "★★★", "actual": "0.30%", "forecast": "0.60%", "previous": "0.30%"},
        {"date": "2026-04-02", "time": "08:00", "country": "🇰🇷", "event": "한국 소비자물가지수 (YoY) (3월)", "imp": "★★★", "actual": "2.20%", "forecast": "2.40%", "previous": "2.00%"},
        {"date": "2026-04-02", "time": "10:00", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-02", "time": "21:30", "country": "🇺🇸", "event": "신규 실업수당청구건수", "imp": "★★★", "actual": "202K", "forecast": "212K", "previous": "211K"},

        {"date": "2026-04-03", "time": "00:00", "country": "🇺🇸", "event": "미국 - 부활절 (휴일)", "imp": "★☆☆", "actual": "휴일", "forecast": "-", "previous": "-"},
        {"date": "2026-04-03", "time": "21:30", "country": "🇺🇸", "event": "미국 평균 시간당 임금 (MoM) (3월)", "imp": "★★★", "actual": "0.20%", "forecast": "0.30%", "previous": "0.40%"},
        {"date": "2026-04-03", "time": "21:30", "country": "🇺🇸", "event": "비농업고용지수 (3월)", "imp": "★★★", "actual": "178K", "forecast": "65K", "previous": "-133K"},
        {"date": "2026-04-03", "time": "21:30", "country": "🇺🇸", "event": "실업률 (3월)", "imp": "★★★", "actual": "4.30%", "forecast": "4.40%", "previous": "4.40%"},
        {"date": "2026-04-03", "time": "22:45", "country": "🇺🇸", "event": "서비스 구매관리자지수 (3월)", "imp": "★★☆", "actual": "49.8", "forecast": "51.1", "previous": "51.7"},

        {"date": "2026-04-06", "time": "23:00", "country": "🇺🇸", "event": "ISM 비제조업구매자지수 (3월)", "imp": "★★★", "actual": "54", "forecast": "54.8", "previous": "56.1"},
        {"date": "2026-04-07", "time": "02:00", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-08", "time": "23:30", "country": "🇺🇸", "event": "원유재고", "imp": "★★☆", "actual": "3.081M", "forecast": "-1.000M", "previous": "5.451M"},

        {"date": "2026-04-09", "time": "03:00", "country": "🇺🇸", "event": "연방공개시장위원회(FOMC) 회의록", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-09", "time": "21:30", "country": "🇺🇸", "event": "근원 소비지출물가지수 (MoM) (2월)", "imp": "★★★", "actual": "0.40%", "forecast": "0.40%", "previous": "0.40%"},
        {"date": "2026-04-09", "time": "21:30", "country": "🇺🇸", "event": "근원 개인소비지출 물가지수 (YoY) (2월)", "imp": "★★★", "actual": "3.00%", "forecast": "3.00%", "previous": "3.10%"},
        {"date": "2026-04-09", "time": "21:30", "country": "🇺🇸", "event": "GDP (QoQ) (4분기)", "imp": "★★★", "actual": "0.50%", "forecast": "0.70%", "previous": "4.40%"},
        {"date": "2026-04-09", "time": "21:30", "country": "🇺🇸", "event": "신규 실업수당청구건수", "imp": "★★★", "actual": "219K", "forecast": "210K", "previous": "203K"},

        {"date": "2026-04-10", "time": "10:00", "country": "🇰🇷", "event": "한국 금리 결정 (4월)", "imp": "★★★", "actual": "2.50%", "forecast": "2.50%", "previous": "2.50%"},
        {"date": "2026-04-10", "time": "21:30", "country": "🇺🇸", "event": "소비자물가지수 (MoM) (3월)", "imp": "★★★", "actual": "0.90%", "forecast": "1.00%", "previous": "0.30%"},
        {"date": "2026-04-10", "time": "21:30", "country": "🇺🇸", "event": "근원 소비자물가지수 (MoM) (3월)", "imp": "★★★", "actual": "0.20%", "forecast": "0.30%", "previous": "0.20%"},
        {"date": "2026-04-10", "time": "21:30", "country": "🇺🇸", "event": "소비자물가지수 (YoY) (3월)", "imp": "★★★", "actual": "3.30%", "forecast": "3.40%", "previous": "2.40%"},

        {"date": "2026-04-13", "time": "23:00", "country": "🇺🇸", "event": "기존주택판매 (3월)", "imp": "★★☆", "actual": "3.98M", "forecast": "4.07M", "previous": "4.13M"},
        {"date": "2026-04-14", "time": "21:30", "country": "🇺🇸", "event": "생산자물가지수 (MoM) (3월)", "imp": "★★★", "actual": "0.50%", "forecast": "1.10%", "previous": "0.50%"},
        
        {"date": "2026-04-15", "time": "08:00", "country": "🇰🇷", "event": "한국 실업률 (3월)", "imp": "★★☆", "actual": "2.70%", "forecast": "-", "previous": "2.90%"},
        {"date": "2026-04-15", "time": "19:00", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설 (1)", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-15", "time": "19:00", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설 (2)", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-15", "time": "23:30", "country": "🇺🇸", "event": "원유재고", "imp": "★★☆", "actual": "-0.913M", "forecast": "2.100M", "previous": "3.081M"},

        {"date": "2026-04-16", "time": "21:30", "country": "🇺🇸", "event": "필라델피아 연은 제조업활동지수 (4월)", "imp": "★★☆", "actual": "26.7", "forecast": "10.3", "previous": "18.1"},
        {"date": "2026-04-16", "time": "21:30", "country": "🇺🇸", "event": "신규 실업수당청구건수", "imp": "★★★", "actual": "207K", "forecast": "213K", "previous": "218K"},

        {"date": "2026-04-17", "time": "08:00", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-18", "time": "03:00", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},

        {"date": "2026-04-21", "time": "21:30", "country": "🇺🇸", "event": "소매판매 (MoM) (3월)", "imp": "★★★", "actual": "1.70%", "forecast": "1.40%", "previous": "0.70%"},
        {"date": "2026-04-21", "time": "21:30", "country": "🇺🇸", "event": "근원 소매판매 (MoM) (3월)", "imp": "★★★", "actual": "1.90%", "forecast": "1.40%", "previous": "0.70%"},
        {"date": "2026-04-21", "time": "21:30", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},

        {"date": "2026-04-22", "time": "23:30", "country": "🇺🇸", "event": "원유재고", "imp": "★★☆", "actual": "1.925M", "forecast": "-1.900M", "previous": "-0.913M"},

        {"date": "2026-04-23", "time": "08:00", "country": "🇰🇷", "event": "한국 GDP (YoY) (1분기)", "imp": "★★★", "actual": "3.60%", "forecast": "2.70%", "previous": "1.60%"},
        {"date": "2026-04-23", "time": "08:00", "country": "🇰🇷", "event": "한국 GDP (QoQ) (1분기)", "imp": "★★★", "actual": "1.70%", "forecast": "1.00%", "previous": "-0.20%"},
        {"date": "2026-04-23", "time": "21:30", "country": "🇺🇸", "event": "신규 실업수당청구건수", "imp": "★★★", "actual": "214K", "forecast": "211K", "previous": "208K"},
        {"date": "2026-04-23", "time": "22:45", "country": "🇺🇸", "event": "서비스 구매관리자지수 (4월)", "imp": "★★☆", "actual": "51.3", "forecast": "50.5", "previous": "49.8"},
        {"date": "2026-04-23", "time": "22:45", "country": "🇺🇸", "event": "제조업 구매관리자지수 (4월)", "imp": "★★☆", "actual": "54", "forecast": "52.5", "previous": "52.3"},

        {"date": "2026-04-26", "time": "01:00", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-26", "time": "11:45", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-27", "time": "08:00", "country": "🇺🇸", "event": "미국 대통령 트럼프 연설", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "-"},

        {"date": "2026-04-28", "time": "23:00", "country": "🇺🇸", "event": "CB 소비자신뢰지수 (4월)", "imp": "★★★", "actual": "92.8", "forecast": "89", "previous": "92.2"},
        {"date": "2026-04-29", "time": "23:30", "country": "🇺🇸", "event": "원유재고", "imp": "★★☆", "actual": "-6.234M", "forecast": "0.300M", "previous": "1.925M"},

        {"date": "2026-04-30", "time": "03:00", "country": "🇺🇸", "event": "금리결정 (Interest Rate)", "imp": "★★★", "actual": "3.75%", "forecast": "3.75%", "previous": "3.75%"},
        {"date": "2026-04-30", "time": "03:00", "country": "🇺🇸", "event": "연방공개시장위원회 성명서", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-30", "time": "03:30", "country": "🇺🇸", "event": "FOMC 기자 회견", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-04-30", "time": "08:00", "country": "🇰🇷", "event": "한국 소매판매 (MoM) (3월)", "imp": "★★☆", "actual": "1.80%", "forecast": "-", "previous": "-0.30%"},
        {"date": "2026-04-30", "time": "21:30", "country": "🇺🇸", "event": "GDP (QoQ) (1분기)", "imp": "★★★", "actual": "-", "forecast": "2.20%", "previous": "0.50%"},
        {"date": "2026-04-30", "time": "21:30", "country": "🇺🇸", "event": "근원 개인소비지출 물가지수 (YoY) (3월)", "imp": "★★★", "actual": "-", "forecast": "3.20%", "previous": "3.00%"},
        {"date": "2026-04-30", "time": "21:30", "country": "🇺🇸", "event": "근원 소비지출물가지수 (MoM) (3월)", "imp": "★★★", "actual": "-", "forecast": "0.30%", "previous": "0.40%"},
        {"date": "2026-04-30", "time": "21:30", "country": "🇺🇸", "event": "신규 실업수당청구건수", "imp": "★★★", "actual": "-", "forecast": "213K", "previous": "214K"},

        # --- 2026년 5월 ---
        {"date": "2026-05-01", "time": "22:45", "country": "🇺🇸", "event": "제조업 구매관리자지수 (4월)", "imp": "★★☆", "actual": "-", "forecast": "54", "previous": "54"},
        {"date": "2026-05-01", "time": "23:00", "country": "🇺🇸", "event": "ISM 제조업구매자지수 (4월)", "imp": "★★★", "actual": "-", "forecast": "53.2", "previous": "52.7"},

        {"date": "2026-05-05", "time": "00:00", "country": "🇰🇷", "event": "한국 - 어린이 날 (휴일)", "imp": "★☆☆", "actual": "휴일", "forecast": "-", "previous": "-"},
        {"date": "2026-05-05", "time": "22:45", "country": "🇺🇸", "event": "서비스 구매관리자지수 (4월)", "imp": "★★☆", "actual": "-", "forecast": "51.3", "previous": "49.8"},
        {"date": "2026-05-05", "time": "23:00", "country": "🇺🇸", "event": "신규 주택판매 (3월)", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "587K"},
        {"date": "2026-05-05", "time": "23:00", "country": "🇺🇸", "event": "미국 노동부 JOLTS (구인, 이직 보고서) (3월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "6.882M"},
        {"date": "2026-05-05", "time": "23:00", "country": "🇺🇸", "event": "ISM 비제조업구매자지수 (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "54"},

        {"date": "2026-05-06", "time": "08:00", "country": "🇰🇷", "event": "한국 소비자물가지수 (YoY) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "2.20%"},
        {"date": "2026-05-06", "time": "08:00", "country": "🇰🇷", "event": "한국 소비자물가지수 (MoM) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "0.30%"},
        {"date": "2026-05-06", "time": "21:15", "country": "🇺🇸", "event": "ADP 비농업부문 고용 변화 (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "62K"},

        {"date": "2026-05-07", "time": "21:30", "country": "🇺🇸", "event": "신규 실업수당청구건수", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "-"},

        {"date": "2026-05-08", "time": "21:30", "country": "🇺🇸", "event": "미국 평균 시간당 임금 (MoM) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "0.20%"},
        {"date": "2026-05-08", "time": "21:30", "country": "🇺🇸", "event": "비농업고용지수 (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "178K"},
        {"date": "2026-05-08", "time": "21:30", "country": "🇺🇸", "event": "실업률 (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "4.30%"},

        {"date": "2026-05-11", "time": "23:00", "country": "🇺🇸", "event": "기존주택판매 (4월)", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "3.98M"},

        {"date": "2026-05-12", "time": "21:30", "country": "🇺🇸", "event": "소비자물가지수 (MoM) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "0.90%"},
        {"date": "2026-05-12", "time": "21:30", "country": "🇺🇸", "event": "소비자물가지수 (YoY) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "3.30%"},
        {"date": "2026-05-12", "time": "21:30", "country": "🇺🇸", "event": "근원 소비자물가지수 (MoM) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "0.20%"},

        {"date": "2026-05-13", "time": "08:00", "country": "🇰🇷", "event": "한국 실업률 (4월)", "imp": "★★☆", "actual": "-", "forecast": "-", "previous": "2.70%"},
        {"date": "2026-05-13", "time": "21:30", "country": "🇺🇸", "event": "생산자물가지수 (MoM) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "0.50%"},

        {"date": "2026-05-14", "time": "21:30", "country": "🇺🇸", "event": "소매판매 (MoM) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "1.70%"},
        {"date": "2026-05-14", "time": "21:30", "country": "🇺🇸", "event": "근원 소매판매 (MoM) (4월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "1.90%"},

        {"date": "2026-05-25", "time": "00:00", "country": "🇺🇸", "event": "미국 - 현충일 (휴일)", "imp": "★☆☆", "actual": "휴일", "forecast": "-", "previous": "-"},
        {"date": "2026-05-25", "time": "00:00", "country": "🇰🇷", "event": "한국 - 석가탄신일 (휴일)", "imp": "★☆☆", "actual": "휴일", "forecast": "-", "previous": "-"},
        {"date": "2026-05-28", "time": "10:00", "country": "🇰🇷", "event": "한국 금리 결정 (5월)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "2.50%"},

        # --- 2026년 6월 ---
        {"date": "2026-06-09", "time": "08:00", "country": "🇰🇷", "event": "한국 GDP (QoQ) (1분기 확정)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "1.70%"},
        {"date": "2026-06-09", "time": "08:00", "country": "🇰🇷", "event": "한국 GDP (YoY) (1분기 확정)", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "3.60%"},
        {"date": "2026-06-18", "time": "03:00", "country": "🇺🇸", "event": "미국 금리결정", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "-"},
        {"date": "2026-06-19", "time": "00:00", "country": "🇺🇸", "event": "미국 - Juneteenth (휴일)", "imp": "★☆☆", "actual": "휴일", "forecast": "-", "previous": "-"},

        # --- 2026년 7월 ---
        {"date": "2026-07-03", "time": "00:00", "country": "🇺🇸", "event": "미국 - 삼일절 (독립기념일 대체휴일)", "imp": "★☆☆", "actual": "휴일", "forecast": "-", "previous": "-"},
        {"date": "2026-07-30", "time": "03:00", "country": "🇺🇸", "event": "미국 금리결정", "imp": "★★★", "actual": "-", "forecast": "-", "previous": "-"},
    ]
    # 제공된 텍스트 중 주요 지표들만 샘플링하여 구성했습니다.
    return pd.DataFrame(data)

def calendar_page():
    st.title("📅 경제지표 캘린더")
    st.write("한국(🇰🇷) 및 미국(🇺🇸)의 주요 경제지표 발표 일정입니다.")
    
    # 데이터 로드
    df = get_calendar_data()
    df['date'] = pd.to_datetime(df['date'])
    
    # 1. 월 선택 셀렉트박스
    years = [2026]
    months = ["4월", "5월", "6월", "7월"]
    
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("연도 선택", years)
    with col2:
        selected_month_name = st.selectbox("월 선택", months)
        selected_month = int(selected_month_name.replace("월", ""))

    # 데이터 필터링
    filtered_df = df[(df['date'].dt.year == selected_year) & (df['date'].dt.month == selected_month)]
    filtered_df = filtered_df.sort_values(by=["date", "time"])

    st.divider()
    st.subheader(f"🔍 {selected_year}년 {selected_month}월 주요 일정")

    if filtered_df.empty:
        st.info("해당 월에는 예정된 주요 지표가 없습니다.")
    else:
        # 날짜별로 그룹화하여 표시
        for date, group in filtered_df.groupby(filtered_df['date'].dt.date):
            # 요일 계산
            weekday = ["월", "화", "수", "목", "금", "토", "일"][date.weekday()]
            with st.expander(f"📅 {date.strftime('%m/%d')} ({weekday})", expanded=True):
                # --- 수정된 부분: actual, forecast, previous 컬럼을 포함하도록 변경 ---
                display_group = group[['time', 'country', 'event', 'imp', 'actual', 'forecast', 'previous']].copy()
                
                # 컬럼명 한글로 변경
                display_group.columns = ['시간', '국가', '지표명', '중요도', '실제치', '예측치', '이전치']
                
                # 표 출력
                st.table(display_group)

# --- 실행 로직 ---
if menu == "메인 대시보드":
    main_dashboard()
elif menu == "FOMC":
    fomc_page()
elif menu == "ECB":
    ecb_page()
elif menu == "BOK":
    bok_page()
elif menu == "경제지표 캘린더":
    calendar_page()
