import pdblp
import pandas as pd
import numpy as np

# NumPy 2.0 호환성 패치: np.NaN 참조 오류 방지
if not hasattr(np, "NaN"):
    np.NaN = np.nan

def get_ktb_yields():
    con = pdblp.BCon(host='127.0.0.1', port=8194, timeout=5000)
    con.start()

    try:
        # 1. 커브 구성 종목 벌크 데이터 호출
        df_bulk = con.bulkref('YCGT0173 Index', 'CURVE_TENOR_RATES')
        if df_bulk is None or df_bulk.empty:
            return pd.DataFrame()

        # 2. 1차원 데이터를 리스트로 변환 후 Tenor:Ticker 매핑
        raw_values = df_bulk['value'].tolist()
        tenor_ticker_map = {}
        # 6개씩 끊어서 Tenor(0)와 Ticker(1)를 가져옴
        for i in range(0, len(raw_values), 6):
            if i + 1 < len(raw_values):
                tenor = raw_values[i]
                ticker = raw_values[i+1]
                tenor_ticker_map[tenor] = ticker

        # 3. 분석 대상 테너 및 티커 리스트 생성
        target_tenors = ['1Y', '3Y', '5Y', '10Y', '30Y']
        active_mapping = {tenor_ticker_map[t]: f"KTB {t}" for t in target_tenors if t in tenor_ticker_map}
        bond_tickers = list(active_mapping.keys())

        # 4. 제안하신 필드 호출 (YTM_MID, CHG_NET_1D)
        fields = ['YLD_YTM_MID', 'YLD_CHG_NET_1D']
        df_res = con.ref(bond_tickers, fields)
        
        if df_res is None or df_res.empty:
            return pd.DataFrame()

        # 5. 결과 재구성 (Pivot 시 발생할 수 있는 NaN 이슈 대응)
        df_pivot = df_res.pivot(index='ticker', columns='field', values='value')
        
        # 최종 결과프레임 생성
        df_final = pd.DataFrame(index=[active_mapping[t] for t in bond_tickers])
        
        for ticker, label in active_mapping.items():
            if ticker in df_pivot.index:
                # 수익률 저장 (데이터가 3.141 형태이므로 그대로 사용)
                df_final.loc[label, 'Yield'] = float(df_pivot.loc[ticker, 'YLD_YTM_MID'])
                # 변동폭 저장 (bp 단위)
                df_final.loc[label, 'Net Chg'] = float(df_pivot.loc[ticker, 'YLD_CHG_NET_1D'])

        return df_final

    except Exception as e:
        # 정확한 디버깅을 위해 에러 메시지 출력
        print(f"KTB 로직 실행 오류: {e}")
        return pd.DataFrame()