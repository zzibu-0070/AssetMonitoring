import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time, timedelta, date

# 자동 새로고침 라이브러리
from streamlit_autorefresh import st_autorefresh

# --------------------------------------------------------------------------
# [페이지 설정]
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="목금월 운동회")

# 자동 새로고침 (3분)
count = st_autorefresh(interval=180 * 1000, key="datarefresh")

st.title("🧩 운동회장 Dashboard")

# --------------------------------------------------------------------------
# [사용자 설정] 포트폴리오 정의
# --------------------------------------------------------------------------
MY_PORTFOLIO = {
    "Index": {
        "대표 지수": ["^IXIC", "^DJI", "NQ=F", "SPY"]
    },
    "청팀 - 미래섹터": {
        "양자컴퓨터": ["IONQ", "QBTS", "RGTI"],
        "양자보안": ["PANW", "ARQQ"], 
        "양자통신": ["030200.KS", "NOK", "VZ"],
        "장수과학 & 합성생물학": ["NTLA", "RXRX", "TWST", "DNA", "CRSP", "NVO"],
        "우주경제": ["LMT", "NOC", "RKLB"],
        "우주 쓰레기처리": ["NOC", "RKLB"],
        "무선 전력전송": ["QCOM", "POWI", "WATT"],
        "BCI플랫폼": ["MDT", "ABT", "BSX"],
        "AI 저작권 플랫폼": ["ORCL", "AMZN", "MSFT", "GOOG", "ADBE"],
        "반도체 벨류체인": ["ON", "TER", "TSM", "005930.KS", "ASML"],
        "데이터센터 냉각": ["066570.KS", "SHEL", "096770.KS", "CC", "VRT"],
        "데이터센터 송전": ["FCX", "006260.KS", "CLF", "PKX", "298040.KS", "010120.KS", "267260.KS", "ETN"],
        "해저케이블": ["PRYMY", "TEL"],
        "SMR": ["OKLO", "SMR", "034020.KS", "BWXT", "CCJ"],
        "수소, 암모니아경제": ["BE", "LIN", "APD", "CF", "KBR"],
        "에너지 핀테크": ["ICE", "ENPH", "STEM"],
        "차세대 배터리": ["TSLA", "FLNC", "STEM", "EOSE", "ALB"],
        "디지털 트윈도시": ["NVDA", "035420.KS", "ADSK"],
        "글로벌 인프라": ["ETN", "PWR", "GEV"],
        "지구 생태 복원": ["WM", "RSG", "TTEK"],
        "해양 미세플라스틱": ["XYL", "WM"],
        "해양 온도제어": ["OXY", "FLR", "XOM"],
        "폐플라스틱 리사이클링": ["EMN", "PCT", "LYB"]
    },
    "헷징자산": {
        "광물": ["GLD", "SLV", "HG=F", "GC=F", "SI=F"],
        "달러": ["UUP"],
        "VIX": ["^VIX"],
        "식재료": ["DBA", "CORN", "WEAT"],
        "식량 및 농업": ["ADM", "DE", "CTVA", "CF"],
        "금광 관련주": ["GOLD", "NEM", "AEM", "GDX"],
        "거대 금융기관": ["BLK", "JPM", "BRK.B", "GS", "SPGI"],
        "원유, 가스": ["USO", "UNG"]
    },
    "백팀 - 자금의 안전금고": {
        "전통에너지": ["XOM", "CVX", "SHEL", "SLB", "COP", "TTE"],
        "미래에너지": ["TSLA", "FSLR", "NEE", "ENPH", "BEP"],
        "데이터인프라": ["MSFT", "AMZN", "AVGO", "ANET", "GOOG", "META", "NVDA"],
        "필수소비재": ["PG", "COST", "WMT", "KO", "PEP", "AMZN"],
        "결제시스템": ["V", "MA", "AXP", "PYPL"],
        "명품소비재": ["RACE", "EL"],
        "물과 식량": ["AWK", "XYL", "ECL", "PHO", "ADM", "DE", "CTVA", "CF"]
    }
}

# --------------------------------------------------------------------------
# [스타일 및 CSS]
# --------------------------------------------------------------------------
st.markdown("""
<style>
    .stPlotlyChart { margin-bottom: -20px; }
    div[data-testid="stMetricValue"] { font-size: 1.0rem; }
    div[data-testid="column"] { align-items: end; } 
    
    div[data-testid="stButton"] > button {
        background-color: transparent !important;
        border: none !important;
        font-size: 26px !important;
        color: #555555 !important;
        padding: 0px !important;
        margin-bottom: 3px !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button:hover {
        color: #ff4b4b !important;
    }
    
    h2 {
        color: #424242;
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 10px;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# [상단 컨트롤 바]
# --------------------------------------------------------------------------
col_date, col_btn, col_space, col_time = st.columns([1.2, 0.15, 5.8, 2.5], vertical_alignment="bottom")

with col_date:
    selected_date = st.date_input("📅 조회 날짜", date.today())

with col_btn:
    if st.button('🔄'):
        st.cache_data.clear()
        st.rerun()

with col_space:
    st.empty() 

with col_time:
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.markdown(f"<div style='text-align: right; font-weight: bold; margin-bottom: 5px; font-size: 0.9rem;'>🕒 기준: {now_str} <span style='font-size:0.7em; color:gray;'>(Auto {count})</span></div>", unsafe_allow_html=True)

is_today_selected = (selected_date == date.today())

# --------------------------------------------------------------------------
# [헬퍼 함수 1] 개별 미니 차트 그리기
# --------------------------------------------------------------------------
def create_chart(ticker, df):
    closes = df['Close']
    curr_price = closes.iloc[-1]
    start_price = closes.iloc[0]
    
    min_val = closes.min()
    max_val = closes.max()
    diff = max_val - min_val
    
    if diff == 0:
        padding = min_val * 0.01 
        y_min = min_val - padding
        y_max = max_val + padding
    else:
        center = (max_val + min_val) / 2
        expanded_half_range = (diff / 2) * 1.5
        y_min = center - expanded_half_range
        y_max = center + expanded_half_range

    color = '#ef5350' if curr_price >= start_price else '#42a5f5'

    fig = go.Figure()

    # 라인 차트
    fig.add_trace(go.Scatter(
        x=df.index, y=closes, mode='lines', line=dict(color=color, width=2),
        fill='tozeroy', 
        fillcolor=f"rgba({int(color.lstrip('#')[0:2], 16)}, {int(color.lstrip('#')[2:4], 16)}, {int(color.lstrip('#')[4:6], 16)}, 0.1)"
    ))

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5), 
        height=100, 
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, range=[y_min, y_max], fixedrange=True)
    )
    return fig

# --------------------------------------------------------------------------
# [헬퍼 함수 2] 트리맵 데이터 생성 (Equal Size + 실제 시총 정보 유지)
# --------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def get_weighted_treemap_data(portfolio, target_date, is_today):
    # 1. 모든 티커 수집
    all_tickers = []
    for cat, sectors in portfolio.items():
        for sec, tickers in sectors.items():
            all_tickers.extend(tickers)
    
    unique_tickers = list(set(all_tickers))
    
    # 2. 가격 데이터 다운로드
    try:
        if is_today:
            price_data = yf.download(unique_tickers, period="5d", group_by='ticker', threads=True, progress=False)
        else:
            end_date = target_date + timedelta(days=1)
            price_data = yf.download(unique_tickers, start=target_date, end=end_date, group_by='ticker', threads=True, progress=False)
    except:
        return pd.DataFrame()

    # 3. 환율 정보
    usd_krw = 1350.0 
    usd_jpy = 150.0  
    try:
        ex_data = yf.download(["KRW=X", "JPY=X"], period="5d", progress=False)['Close']
        if not ex_data.empty:
            usd_krw = ex_data['KRW=X'].iloc[-1]
            usd_jpy = ex_data['JPY=X'].iloc[-1]
    except:
        pass

    # 4. 시가총액 데이터 다운로드
    caps = {}
    tickers_obj = yf.Tickers(" ".join(unique_tickers))
    
    for t in unique_tickers:
        try:
            info = tickers_obj.tickers[t].fast_info
            raw_cap = info.get('market_cap', 0)
            currency = info.get('currency', 'USD')
            
            if raw_cap is None: raw_cap = 0
            
            if currency == 'KRW':
                cap = raw_cap / usd_krw
            elif currency == 'JPY':
                cap = raw_cap / usd_jpy
            else:
                cap = raw_cap 
                
            caps[t] = cap
        except:
            caps[t] = 0

    # 5. 계층 구조 빌드 (Bottom-Up)
    leaf_nodes = []
    
    # 집계용 딕셔너리
    # cap: 실제 시총 (성적 가중치 계산용)
    # visual_cap: 화면 표시용 크기 (무조건 1)
    # weighted_sum: 등락률 * 실제 시총 (여전히 돈의 흐름 기준 성적 계산)
    sector_aggs = {}   
    category_aggs = {} 
    
    for category, sectors in portfolio.items():
        if category not in category_aggs:
            category_aggs[category] = {'cap': 0, 'visual_cap': 0, 'weighted_sum': 0}
            
        for sector, tickers in sectors.items():
            sec_key = f"{category}/{sector}"
            if sec_key not in sector_aggs:
                sector_aggs[sec_key] = {'cap': 0, 'visual_cap': 0, 'weighted_sum': 0, 'parent': category, 'name': sector}
            
            for ticker in tickers:
                # A. 실제 시총 (USD) - 데이터가 없으면 10M으로 가정
                real_cap = caps.get(ticker, 0)
                if real_cap == 0: real_cap = 10000000 
                
                # [수정] 모든 타일의 크기를 1로 고정
                visual_size = 1

                # C. 등락률 계산
                pct_change = 0.0
                try:
                    if len(unique_tickers) > 1:
                        df = price_data[ticker]
                    else:
                        df = price_data
                        
                    if not df.empty and not df['Close'].isna().all():
                        if is_today:
                            closes = df['Close'].dropna()
                            if len(closes) >= 2:
                                pct_change = ((closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2]) * 100
                            elif len(closes) == 1:
                                open_p = df['Open'].dropna().iloc[-1]
                                if open_p != 0: pct_change = ((closes.iloc[-1] - open_p) / open_p) * 100
                        else:
                            row = df.dropna().iloc[0]
                            if row['Open'] != 0:
                                pct_change = ((row['Close'] - row['Open']) / row['Open']) * 100
                except:
                    pct_change = 0.0
                
                leaf_nodes.append({
                    'id': ticker,
                    'parent': sec_key,
                    'value': visual_size,       # 크기: 1 (고정)
                    'real_value': real_cap,     # 호버: 실제 시총
                    'change': pct_change,
                    'label': f"{ticker}<br>{pct_change:.2f}%"
                })
                
                # 상위 집계
                # 화면 크기는 갯수만큼(visual_size) 더하지만, 
                # 등락률 성적은 '돈(real_cap)' 비중을 유지합니다 (금융 표준)
                sector_aggs[sec_key]['cap'] += real_cap
                sector_aggs[sec_key]['visual_cap'] += visual_size
                sector_aggs[sec_key]['weighted_sum'] += (pct_change * real_cap)
                
                category_aggs[category]['cap'] += real_cap
                category_aggs[category]['visual_cap'] += visual_size
                category_aggs[category]['weighted_sum'] += (pct_change * real_cap)

    # (2) 섹터 노드 생성
    sector_nodes = []
    for sec_key, data in sector_aggs.items():
        total_cap = data['cap']
        total_visual = data['visual_cap'] # 종목 갯수 합
        
        avg_change = data['weighted_sum'] / total_cap if total_cap > 0 else 0
        
        sector_nodes.append({
            'id': sec_key,
            'parent': data['parent'],
            'value': total_visual,      
            'real_value': total_cap,    
            'change': avg_change,
            'label': f"{data['name']}<br>{avg_change:.2f}%"
        })

    # (3) 카테고리 노드 생성
    category_nodes = []
    root_cap = 0
    root_visual = 0
    root_weighted_sum = 0
    
    for cat_key, data in category_aggs.items():
        total_cap = data['cap']
        total_visual = data['visual_cap']
        avg_change = data['weighted_sum'] / total_cap if total_cap > 0 else 0
        
        category_nodes.append({
            'id': cat_key,
            'parent': "운동회장",
            'value': total_visual,
            'real_value': total_cap,
            'change': avg_change,
            'label': f"{cat_key}<br>{avg_change:.2f}%"
        })
        root_cap += total_cap
        root_visual += total_visual
        root_weighted_sum += data['weighted_sum']

    # (4) 루트 노드
    root_change = root_weighted_sum / root_cap if root_cap > 0 else 0
    root_node = [{
        'id': "운동회장",
        'parent': "",
        'value': root_visual,
        'real_value': root_cap,
        'change': root_change,
        'label': f"전체 시장<br>{root_change:.2f}%"
    }]
    
    all_data = root_node + category_nodes + sector_nodes + leaf_nodes
    return pd.DataFrame(all_data)

# --------------------------------------------------------------------------
# [메인 로직]
# --------------------------------------------------------------------------

tab1, tab2 = st.tabs(["Treemap", "Charts"])

# --- TAB 1: 트리맵 ---
with tab1:
    st.markdown("##### 💡 모든 종목을 동일한 크기(Equal Size)로 표시합니다.")
    if st.button("전광판 새로고침", key="tree_refresh"):
        st.cache_data.clear()
        st.rerun() 
        
    with st.spinner("선수들의 체급(동일)과 성적(등락)을 계산 중입니다..."):
        df_tree = get_weighted_treemap_data(MY_PORTFOLIO, selected_date, is_today_selected)
    
    if not df_tree.empty:
        fig = go.Figure(go.Treemap(
            ids=df_tree['id'],
            labels=df_tree['label'],
            parents=df_tree['parent'],
            values=df_tree['value'],          # 크기 결정: 1 (고정)
            customdata=df_tree['real_value'], # 호버 표시용: 실제 값 (real_cap)
            marker=dict(
                colors=df_tree['change'],
                colorscale=['#42a5f5', '#eeeeee', '#ef5350'],
                cmid=0,
                cmin=-3, 
                cmax=3,
                showscale=True,
                colorbar=dict(title="등락률(%)")
            ),
            textinfo="label",
            # %{value} 대신 %{customdata}를 사용하여 실제 시총 표시
            hovertemplate='<b>%{label}</b><br>시가총액(USD): $%{customdata:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            margin=dict(t=10, l=10, r=10, b=10), 
            height=700,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("데이터를 불러오는 중입니다. 잠시만 기다려주세요.")

# --- TAB 2: 차트 그리드 (기존 동일) ---
with tab2:
    for category, sectors in MY_PORTFOLIO.items():
        st.header(f"{category}")
        
        for sector, tickers in sectors.items():
            st.subheader(f"{sector}")
            cols = st.columns(5)
            
            for idx, ticker in enumerate(tickers):
                with cols[idx % 5]:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = pd.DataFrame()

                        if is_today_selected:
                            hist = stock.history(period="1d", interval="5m")
                            if hist.empty:
                                recent_hist = stock.history(period="5d", interval="5m")
                                if not recent_hist.empty:
                                    last_trade_date = recent_hist.index[-1].date()
                                    hist = recent_hist[recent_hist.index.date == last_trade_date]
                        else:
                            start_dt = datetime.combine(selected_date, datetime.min.time())
                            end_dt = start_dt + timedelta(days=1)
                            days_diff = (datetime.now() - start_dt).days
                            interval = "5m" if days_diff < 59 else "60m"
                            hist = stock.history(start=start_dt, end=end_dt, interval=interval)

                        if hist.empty:
                            st.warning(f"{ticker}: N/A")
                            continue

                        curr = hist['Close'].iloc[-1]
                        prev_close = stock.info.get('previousClose', None)
                        if prev_close is None:
                            prev_close = hist['Open'].iloc[0]
                        
                        shown_date = hist.index[-1].date()
                        
                        if shown_date != date.today():
                             ref_price = hist['Open'].iloc[0]
                             label_suffix = f"({shown_date.strftime('%m/%d')})"
                        else:
                             ref_price = prev_close
                             label_suffix = ""

                        diff = curr - ref_price
                        pct = (diff / ref_price) * 100 if ref_price != 0 else 0
                        
                        st.metric(
                            label=f"{ticker} {label_suffix}",
                            value=f"${curr:,.2f}",
                            delta=f"{diff:.2f} ({pct:.2f}%)"
                        )
                        
                        chart = create_chart(ticker, hist)
                        unique_key = f"chart_{category}_{sector}_{ticker}_{idx}"
                        st.plotly_chart(chart, use_container_width=True, config={'staticPlot': True}, key=unique_key)

                    except Exception as e:
                        st.caption(f"⚠️ {ticker} 로딩 실패")
            st.write("") 
        st.divider()