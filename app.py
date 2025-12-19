import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time, timedelta, date
import pytz

# [추가됨] 자동 새로고침 라이브러리
# 설치 필요: pip install streamlit-autorefresh
from streamlit_autorefresh import st_autorefresh

# --------------------------------------------------------------------------
# [페이지 설정]
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="목금월 운동회장")

# [핵심] 자동 새로고침 설정 (interval: 밀리초 단위)
# 180 * 1000 = 180,000ms = 3분
# key는 이 타이머의 고유 이름입니다.
count = st_autorefresh(interval=180 * 1000, key="datarefresh")

st.title("운동회장")

# --------------------------------------------------------------------------
# [사용자 설정] 3단 구조 (카테고리 > 섹터 > 종목)
# --------------------------------------------------------------------------
MY_PORTFOLIO = {
    "Index": {
        "대표 지수": ["^IXIC", "^DJI", "NQ=F", "SPY"]
    },
    "청팀 - 미래섹터": {
        "양자컴퓨터&보안": ["IONQ", "QBTS", "SKM", "RGTI"],
        "장수과학 & 합성생물학": ["NTLA", "RXRX", "TWST", "DNA", "CRSP"],
        "AI 저작권 플랫폼": ["ORCL", "AMZN", "MSFT", "GOOG", "ADBE"],
        "반도체 벨류체인": ["ON", "TER", "TSM", "005930.KS", "ASML"],
        "데이터센터 냉각": ["066570.KS", "SHEL", "096770.KS", "CC", "VRT"],
        "데이터센터 송전": ["FCX", "006260.KS", "CLF", "PKX", "298040.KS", "010120.KS", "267260.KS", "ETN"],
        "SMR": ["OKLO", "SMR", "034020.KS"],
        "수소, 암모니아경제": ["BE", "LIN", "APD", "CF", "KBR"],
        "차세대 배터리": ["TSLA", "FLNC", "STEM", "EOSE"],
        "디지털 트윈도시": ["NVDA", "035420.KS"]
    },
    "헷징자산": {
        "광물": ["GLD", "SLV"],
        "식재료": ["DBA", "CORN", "WEAT"],
        "식량 및 농업": ["ADM", "DE", "CTVA", "CF"],
        "금광 관련주": ["GOLD", "NEM", "AEM", "GDX"],
        "원유, 가스": ["USO", "UNG"]
    },
    "백팀 - 자금의 안전금고": {
        "전통에너지": ["XOM", "CVX", "SHEL", "SLB"],
        "미래에너지": ["TSLA", "FSLR", "NEE", "ENPH"],
        "데이터인프라": ["MSFT", "AMZN", "AVGO", "ANET", "GOOG", "META", "NVDA"],
        "필수소비재": ["PG", "COST", "WNT", "KO", "PEP", "AMZN"],
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

with col_space:
    st.empty() 

with col_time:
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 자동 갱신 카운트를 작게 표시해서 작동 중임을 알려줌 (선택사항)
    st.markdown(f"<div style='text-align: right; font-weight: bold; margin-bottom: 5px; font-size: 0.9rem;'>🕒 기준: {now_str} <span style='font-size:0.7em; color:gray;'>(Auto {count})</span></div>", unsafe_allow_html=True)

is_today_selected = (selected_date == date.today())

# --------------------------------------------------------------------------
# [헬퍼 함수] 차트 그리기 (Y축 1.5배 & 가변 X축)
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
# [메인 로직]
# --------------------------------------------------------------------------
# 자동 갱신 시 캐시된 데이터가 아닌 새 데이터를 받아와야 하므로
# 이전에 받아온 캐시를 비우는 로직이 필요할 수 있습니다.
# 하지만 st_autorefresh는 단순히 페이지를 '새로고침'하는 역할이므로,
# yfinance 함수 내부의 캐싱(@st.cache_data)을 ttl(유효기간)로 관리하는 것이 좋습니다.

# [중요] 기존 코드에 @st.cache_data가 없었거나 ttl 설정을 안 했다면
# 매번 다운로드하므로 속도는 느리지만 최신 데이터는 보장됩니다.
# API 보호를 위해 캐싱을 씌우고 ttl을 180초로 맞추는 것을 추천합니다.

# 여기서는 직관성을 위해 캐싱 없이 매번 호출하되 3분 간격을 둡니다.

for category, sectors in MY_PORTFOLIO.items():
    st.header(f"{category}")
    
    for sector, tickers in sectors.items():
        st.subheader(f"{sector}")
        cols = st.columns(4)
        
        for idx, ticker in enumerate(tickers):
            with cols[idx % 4]:
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
                    prev_close = stock.info.get('previousClose', hist['Open'].iloc[0])
                    
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
                    
                    st.plotly_chart(
                        chart, 
                        use_container_width=True, 
                        config={'staticPlot': True},
                        key=unique_key
                    )

                except Exception as e:
                    st.error(f"Error: {ticker}")
        
        st.write("") 
    st.divider()