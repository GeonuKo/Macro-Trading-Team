import streamlit as st
import pandas as pd
import numpy as np
import UST
import KTB

# 페이지 설정
st.set_page_config(page_title="하나증권 외화운용실", layout="wide", initial_sidebar_state="expanded")

# 세션 상태 초기화
if 'menu' not in st.session_state:
    st.session_state.menu = "Main"

# 라디오 버튼 상호 간섭을 막기 위한 콜백 함수
def update_market():
    st.session_state.menu = st.session_state.market_radio

def update_cb():
    st.session_state.menu = st.session_state.cb_radio


#  사이드바 구성
with st.sidebar:
    st.title("외화운용실")
    st.markdown("---")

    # --- 1. Main ---
    if st.button("🏠 Main", use_container_width=True):
        st.session_state.menu = "Main"

    # --- 2. Markets ---
    is_market = st.session_state.menu in ["Equities", "Bonds", "Currencies", "Commodities"]
    with st.expander("📊 Markets", expanded=is_market):
        try:
            m_index = ["Equities", "Bonds", "Currencies", "Commodities"].index(st.session_state.menu)
        except ValueError:
            m_index = 0
            
        st.radio(
            "Market Submenu",
            ["Equities", "Bonds", "Currencies", "Commodities"],
            key="market_radio",
            index=m_index,
            on_change=update_market,
            label_visibility="collapsed"
        )

    # --- 3. Central Banks ---
    is_cb = st.session_state.menu in ["Fed", "ECB", "BOK"]
    with st.expander("🏛️ Central Banks", expanded=is_cb):
        try:
            c_index = ["Fed", "ECB", "BOK"].index(st.session_state.menu)
        except ValueError:
            c_index = 0

        st.radio(
            "CB Submenu",
            ["Fed", "ECB", "BOK"],
            key="cb_radio",
            index=c_index,
            on_change=update_cb,
            label_visibility="collapsed"
        )

    # --- 4. Economic Calendar ---
    if st.button("📅 Economic Calendar", use_container_width=True):
        st.session_state.menu = "Economic Calendar"

# Bonds 페이지
def bonds_page():
    st.title("💵 채권 및 금리 분석 (Bonds)")
    st.markdown("전 세계 국채 시장의 실시간 금리 현황입니다.")

    # --- [미국 국채 섹션] ---
    st.subheader("🇺🇸 US Treasury Yields")
    try:
        df_ust = UST.get_ust_yields()
        if not df_ust.empty:
            cols = st.columns(7)
            tenors = ["UST 1Y", "UST 2Y", "UST 5Y", "UST 10Y", "UST 30Y"]
            
            # 각 테너별 Metric 표시
            for i, tenor in enumerate(tenors):
                with cols[i]:
                    yld = df_ust.loc[tenor, "Yield (%)"]
                    chg = df_ust.loc[tenor, "Net Chg (bp)"]
                    st.metric(
                        label=tenor, 
                        value=f"{yld:.3f}%", 
                        delta=f"{chg:+.1f} bp", 
                        delta_color="inverse"
                    )
            
            # Spread 계산 (UST)
            with cols[5]:
                # 10Y - 2Y Spread
                spr_10_2 = (df_ust.loc["UST 10Y", "Yield (%)"] - df_ust.loc["UST 2Y", "Yield (%)"]) * 100
                st.metric(label="10Y-2Y", value=f"{spr_10_2:.1f} bp")
                
            with cols[6]:
                # 30Y - 5Y Spread
                spr_30_5 = (df_ust.loc["UST 30Y", "Yield (%)"] - df_ust.loc["UST 5Y", "Yield (%)"]) * 100
                st.metric(label="30Y-5Y", value=f"{spr_30_5:.1f} bp")
        else:
            st.warning("미국 국채 데이터를 가져올 수 없습니다.")
            
    except Exception as e:
        st.error(f"미국 데이터 호출 오류: {e}")

    st.markdown("---")

    st.subheader("🇰🇷 Korea Treasury Yields")
    try:
        df_ktb = KTB.get_ktb_yields()
        if not df_ktb.empty:
            # 총 7개의 컬럼 생성 (금리 5개 + 스프레드 2개)
            cols = st.columns(7)
            
            # 1. 국채 금리 표시 (Column 0 ~ 4)
            tenors_kr = ["KTB 1Y", "KTB 3Y", "KTB 5Y", "KTB 10Y", "KTB 30Y"]
            for i, tenor in enumerate(tenors_kr):
                with cols[i]:
                    yld = df_ktb.loc[tenor, "Yield"]
                    raw_chg = df_ktb.loc[tenor, "Net Chg"]
                    
                    # 변동폭 처리
                    if pd.isna(raw_chg):
                        delta_val = "N/A"
                    else:
                        bp_chg = raw_chg
                        delta_val = f"{bp_chg:+.1f} bp"
                    
                    st.metric(label=tenor, value=f"{yld:.3f}%", delta=delta_val, delta_color="inverse")

            # 2. 스프레드 계산 및 표시 (Column 5 ~ 6)
            y3 = df_ktb.loc["KTB 3Y", "Yield"]
            y10 = df_ktb.loc["KTB 10Y", "Yield"]
            y30 = df_ktb.loc["KTB 30Y", "Yield"]

            with cols[5]:
                spr_10_3 = (y10 - y3) * 100
                st.metric(label="10Y-3Y", value=f"{spr_10_3:.1f} bp")

            with cols[6]:
                spr_30_10 = (y30 - y10) * 100
                st.metric(label="30Y-10Y", value=f"{spr_30_10:.1f} bp")

        else:
            st.warning("한국 국채 데이터를 불러올 수 없습니다.")
    except Exception as e:
        st.error(f"대시보드 표시 오류: {e}")

# 메인 화면 로직

target = st.session_state.menu

if target == "Main":
    st.header("🏠 메인 대시보드")
    # main_dashboard_page()
    
elif target == "Equities":
    st.header("📈 주식(Equities)")
    
elif target == "Bonds":
    bonds_page()
    
elif target == "Currencies":
    st.header("💱 외환 시장(Currencies)")
    
elif target == "Commodities":
    st.header("🛢️ 원자재(Commodities)")

elif target == "Fed":
    st.header("🇺🇸 연방준비제도(Fed)")
    
elif target == "ECB":
    st.header("🇪🇺 유럽중앙은행(ECB)")
    
elif target == "BOK":
    st.header("🇰🇷 한국은행(BOK)")

elif target == "Economic Calendar":
    st.header("📅 경제지표 캘린더")

