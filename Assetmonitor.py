import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, time, timedelta, date

# 자동 새로고침 라이브러리
from streamlit_autorefresh import st_autorefresh

# --------------------------------------------------------------------------
# [페이지 설정]
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="목금월 운동회")

# 자동 새로고침 (3분 = 180초)
count = st_autorefresh(interval=180 * 1000, key="datarefresh")

st.title("🧩 운동회장")

# --------------------------------------------------------------------------
# [사용자 설정] 포트폴리오 정의
# --------------------------------------------------------------------------
MY_PORTFOLIO = {
    "Index": {
        "대표 지수": ["^IXIC", "^DJI", "NQ=F", "SPY"]
    },
    "청팀 - 미래섹터": {
        "양자컴퓨터": ["IONQ", "QBTS", "SKM", "RGTI"],
        "양자보안": ["PANW", "THLLY", "ARQQ"],
        "양자통신": ["030200.KS", "NOK", "VZ"],
        "장수과학 & 합성생물학": ["NTLA", "RXRX", "TWST", "DNA", "CRSP", "NVO"],
        "우주경제": ["LMT", "NOC", "RKLB"],
        "우주 쓰레기처리": ["NOC", "RKLB", "186A.JP"],
        "무선 전력전송": ["QCOM", "POWI", "WATT"],
        "BCI플랫폼": ["MDT", "ABT", "BSX"],
        "AI 저작권 플랫폼": ["ORCL", "AMZN", "MSFT", "GOOG", "ADBE"],
        "반도체 벨류체인": ["ON", "TER", "TSM", "005930.KS", "ASML"],
        "데이터센터 냉각": ["066570.KS", "SHEL", "096770.KS", "CC", "VRT"],
        "데이터센터 송전": ["FCX", "006260.KS", "CLF", "PKX", "298040.KS", "010120.KS", "267260.KS", "ETN"],
        "해저케이블": ["PRYMY", "6701.JP", "TEL"],
        "SMR": ["OKLO", "SMR", "034020.KS", "BWXT", "CCJ"],
        "수소, 암모니아경제": ["BE", "LIN", "APD", "CF", "KBR"],
        "에너지 핀테크": ["ICE", "ENPH", "STEM"],
        "차세대 배터리": ["TSLA", "FLNC", "STEM", "EOSE", "ALB"],
        "디지털 트윈도시": ["NVDA", "035420.KS", "DASTY", "ADSK"],
        "글로벌 인프라(전력망/전환)": ["ETN", "PWR", "GEV"],
        "지구 생태 복원": ["WN", "RSG", "TTEK"],
        "해양 미세플라스틱 로봇": ["XYL", "VEOEY", "WM"],
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
        "결제시스템": ["V", "MA", "AXP", "XYZ", "PYPL"],
        "명품소비재": ["LVMUY", "HESAY", "RACE", "CFRUY", "EL"],
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
# [헬퍼 함수 1] 개별 차트 그리기
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

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, 
        row_heights=[0.75, 0.25], specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )

    fig.add_trace(go.Scatter(
        x=df.index, y=closes, mode='lines', line=dict(color=color, width=2),
        fill='tozeroy', fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.05,)}"
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], marker_color='lightgray', opacity=0.3
    ), row=2, col=1)

    if not df.empty:
        base_dt = df.index[0]
        base_date = base_dt.date()
        base_tz = base_dt.tzinfo 
        market_open = datetime.combine(base_date, time(9, 30)).replace(tzinfo=base_tz)
        market_mid  = datetime.combine(base_date, time(13, 0)).replace(tzinfo=base_tz) 
        market_close = datetime.combine(base_date, time(16, 0)).replace(tzinfo=base_tz)
        
        last_data_time = df.index[-1]
        
        if last_data_time < market_mid:
            x_range = [market_open, market_mid]
        else:
            x_range = [market_open, market_close]
    else:
        x_range = None

    fig.update_layout(
        margin=dict(l=40, r=10, t=10, b=0), height=240, showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_yaxes(
        range=[y_min, y_max], visible=True, showgrid=True, gridcolor='rgba(200,200,200,0.2)',
        tickfont=dict(size=10, color='gray'), row=1, col=1
    )
    fig.update_yaxes(visible=False, row=2, col=1)
    fig.update_xaxes(
        visible=True, row=2, col=1, tickformat="%H:%M",
        dtick=7200000, showgrid=False, tickfont=dict(size=9, color='gray'),
        range=x_range
    )
    fig.update_xaxes(visible=False, row=1, col=1, range=x_range)
    return fig

# --------------------------------------------------------------------------
# [헬퍼 함수 2] 트리맵 데이터 준비 (업그레이드된 로직)
# --------------------------------------------------------------------------
@st.cache_data(ttl=180) 
def get_treemap_data(portfolio, target_date, is_today):
    tickers_list = []
    rows = []
    
    for category, sectors in portfolio.items():
        for sector, tickers in sectors.items():
            for ticker in tickers:
                tickers_list.append(ticker)
                rows.append({
                    "Category": category,
                    "Sector": sector,
                    "Ticker": ticker,
                    "Size": 1 
                })
    
    unique_tickers = list(set(tickers_list))
    if not unique_tickers:
        return pd.DataFrame()
        
    try:
        # 오늘 날짜인 경우, 전일 종가를 알기 위해 5일치를 넉넉히 가져옴
        period_arg = "5d" if is_today else None
        start_arg = None if is_today else target_date
        end_arg = None if is_today else target_date + timedelta(days=1)
        
        if is_today:
            data = yf.download(unique_tickers, period=period_arg, group_by='ticker', threads=True)
        else:
            data = yf.download(unique_tickers, start=start_arg, end=end_arg, group_by='ticker', threads=True)

        final_rows = []
        for row in rows:
            ticker = row['Ticker']
            try:
                if len(unique_tickers) > 1:
                    df = data[ticker]
                else:
                    df = data
                
                # 데이터가 아예 없거나, 종가 컬럼이 모두 비어있으면 건너뜀
                if df.empty or df['Close'].isna().all():
                    continue
                
                pct_change = 0.0
                
                # [로직 개선 포인트]
                if is_today:
                    recent_closes = df['Close'].dropna()
                    if len(recent_closes) >= 2:
                        # 데이터가 충분하면: (현재가 - 전일종가) / 전일종가
                        curr = recent_closes.iloc[-1]
                        prev = recent_closes.iloc[-2]
                        pct_change = ((curr - prev) / prev) * 100
                    elif len(recent_closes) == 1:
                        # 장 시작 직후라 데이터가 1개뿐이면: (현재가 - 시가) / 시가
                        # 혹은 이전 데이터가 없어서 시가 대비로 계산
                        curr = recent_closes.iloc[-1]
                        open_p = df['Open'].dropna().iloc[-1]
                        if open_p != 0:
                            pct_change = ((curr - open_p) / open_p) * 100
                else:
                    # 과거 날짜 조회 (기존 로직 유지)
                    daily_data = df.dropna()
                    if not daily_data.empty:
                        open_price = daily_data['Open'].iloc[0]
                        close_price = daily_data['Close'].iloc[0]
                        if open_price != 0:
                            pct_change = ((close_price - open_price) / open_price) * 100

                row['Change'] = pct_change
                row['Label'] = f"{ticker}<br>{pct_change:.2f}%"
                final_rows.append(row)
                
            except Exception:
                continue
                
        return pd.DataFrame(final_rows)
        
    except Exception as e:
        st.error(f"데이터 다운로드 실패: {e}")
        return pd.DataFrame()

# --------------------------------------------------------------------------
# [메인 로직]
# --------------------------------------------------------------------------

tab1, tab2 = st.tabs(["Treemap", "Charts"])

# --- TAB 1: 트리맵 뷰 ---
with tab1:
    st.subheader("운동회 전광판")
    # 버튼 누르면 캐시 비우고 즉시 리런
    if st.button("지도 데이터 새로고침", key="tree_refresh"):
        st.cache_data.clear()
        st.rerun() 
        
    with st.spinner("경기 데이터를 모으는 중..."):
        df_tree = get_treemap_data(MY_PORTFOLIO, selected_date, is_today_selected)
    
    if not df_tree.empty:
        fig = px.treemap(
            df_tree, 
            path=[px.Constant("운동회장"), 'Category', 'Sector', 'Ticker'], 
            values='Size', 
            color='Change',
            color_continuous_scale=['#42a5f5', '#eeeeee', '#ef5350'],
            color_continuous_midpoint=0, 
            range_color=[-3, 3], 
            custom_data=['Change']
        )
        fig.update_traces(
            textinfo="label+text",
            texttemplate="%{label}<br>%{customdata[0]:.2f}%",
            textfont=dict(size=14),
            hovertemplate='<b>%{label}</b><br>등락률: %{customdata[0]:.2f}%'
        )
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=700)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("데이터가 없습니다.")

# --- TAB 2: 차트 뷰 (5열 그리드 방식) ---
with tab2:
    for category, sectors in MY_PORTFOLIO.items():
        st.header(f"{category}")
        
        for sector, tickers in sectors.items():
            st.subheader(f"{sector}")
            
            # 5열 그리드
            cols = st.columns(5)
            
            for idx, ticker in enumerate(tickers):
                with cols[idx % 5]:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = pd.DataFrame()

                        if is_today_selected:
                            hist = stock.history(period="1d", interval="5m")
                            if hist.empty: # 장 시작 전이거나 데이터 없을 때
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
                        
                        # 전일 종가 가져오기 (info 활용 시도 -> 실패시 시가 사용)
                        prev_close = stock.info.get('previousClose', None)
                        if prev_close is None:
                            prev_close = hist['Open'].iloc[0]
                        
                        shown_date = hist.index[-1].date()
                        
                        if shown_date != date.today():
                             # 과거 데이터면 시가를 기준점으로
                             ref_price = hist['Open'].iloc[0]
                             label_suffix = f"({shown_date.strftime('%m/%d')})"
                        else:
                             # 오늘 데이터면 전일 종가를 기준점으로
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
                        st.error(f"Error: {ticker}")
            st.write("") 
        st.divider()