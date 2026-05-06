import pdblp
import pandas as pd

def get_ust_yields():
    """
    블룸버그로부터 미국 국채 주요 테너(Active Treasury)의 금리 데이터를 가져옵니다.
    """
    # 1. 블룸버그 연결 설정
    con = pdblp.BCon(host='127.0.0.1', port=8194, timeout=5000)
    con.start()

    # 2. 요청하신 티커 리스트 정의 (Govt 태그 사용)
    # CT는 Current(최근발행물)를 의미하며, 뒤의 숫자는 테너를 나타냅니다.
    tickers = {
        "CB12 Govt": "UST 1Y",
        "CT2 Govt": "UST 2Y",
        "CT5 Govt": "UST 5Y",
        "CT10 Govt": "UST 10Y",
        "CT30 Govt": "UST 30Y"
    }
    
    # 3. 데이터 호출 
    fields = ['YLD_YTM_MID', 'YLD_CHG_NET_1D']
    
    # 4. 데이터프레임 생성 및 가공
    df = con.ref(list(tickers.keys()), fields)
    
    # 데이터가 비어있을 경우를 대비한 처리
    if df.empty:
        return pd.DataFrame()

    # Pivot 테이블로 변환
    df_pivot = df.pivot(index='ticker', columns='field', values='value')
    
    # 인덱스명을 설정하신 한글 이름으로 변경
    df_pivot.index = df_pivot.index.map(tickers)
    
    # 컬럼 이름 변경 (PX_LAST -> 금리, CHG_NET_1D -> 변동)
    df_pivot.columns = ['Net Chg (bp)', 'Yield (%)']
    
    # 테너 순서대로 정렬
    sorter = ["UST 1Y", "UST 2Y", "UST 5Y", "UST 10Y", "UST 30Y"]
    df_pivot = df_pivot.reindex(sorter)
    
    return df_pivot