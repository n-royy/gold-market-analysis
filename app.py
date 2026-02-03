import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from gold_tracker.data_fetcher import get_global_gold_price, get_usd_vnd_rate, get_sjc_gold_price, fetch_gold_news
from gold_tracker.calculator import calculate_converted_global_price, calculate_gap
from gold_tracker.llm_analyzer import get_gold_market_analysis
from gold_tracker.storage import save_snapshot, get_history, init_db

# Load env
load_dotenv()

st.set_page_config(page_title="Vietnam Gold Tracker AI", page_icon="img/logo.png", layout="wide")

# Initialize DB
init_db()

st.title("Vietnam Gold Price Tracker & AI Forecaster")
st.markdown("Theo dõi giá vàng theo thời gian thực, quy đổi và phân tích thị trường bằng trí tuệ nhân tạo.")

# Main Logic
if st.button("🔄 Cập nhật dữ liệu ngay"):
    st.cache_data.clear()
    st.rerun()

st.caption("Tự động cập nhật mỗi 5 phút.")
@st.cache_data(ttl=300)  # Cache data for 5 minutes
def fetch_data():
    global_price = get_global_gold_price()
    exchange_rate = get_usd_vnd_rate()
    sjc_data = get_sjc_gold_price()
    news = fetch_gold_news()
    
    # Mock fallbacks if fetch fails
    if global_price is None: global_price = 2600.0
    if exchange_rate is None: exchange_rate = 25400.0
    if sjc_data is None: sjc_data = {'buy': 83000000, 'sell': 85000000}
    
    return global_price, exchange_rate, sjc_data, news

# Fetch Data
global_price, exchange_rate, sjc_data, news = fetch_data()

# Calculate
converted_price = calculate_converted_global_price(global_price, exchange_rate)
gap = calculate_gap(sjc_data['sell'], converted_price)

# Tự động lưu snapshot khi dữ liệu thay đổi đáng kể hoặc mỗi 5 phút
if 'last_save' not in st.session_state or (pd.Timestamp.now() - st.session_state.last_save).seconds > 300:
    save_snapshot({
        "global_price": global_price,
        "exchange_rate": exchange_rate,
        "sjc_sell": sjc_data['sell'],
        "sjc_buy": sjc_data['buy'],
        "converted_price": converted_price,
        "gap": gap,
        "ai_report": "" # No report for auto-saves
    })
    st.session_state.last_save = pd.Timestamp.now()

# Display Metrics
# Row 1
col1, col2 = st.columns(2)
with col1:
    st.metric("Giá vàng quốc tế:", f"${global_price:,.2f}/lượng", border=True)
with col2:
    st.metric("USD/VND Rate", f"{exchange_rate:,.0f} VND", border=True)
# Row 2
col3, col4 = st.columns(2)
with col3:
    st.metric("Giá vàng bán ra của SJC:", f"{sjc_data['sell']:,.0f} VND", border=True)
with col4:
    st.metric("Giá vàng mua vào SJC:", f"{sjc_data['buy']:,.0f} VND", border=True)
# Row 3
col5, col6 = st.columns(2)
with col5:
    st.metric("Quy đổi giá vàng thế giới sang tiền Việt", f"{converted_price:.2f} Triệu VND", border=True)
with col6:
    st.metric("Chênh lệnh", f"{gap:.2f} Triệu VND", delta_color="inverse", border=True)

st.divider()

# Charts & Analysis
row1 = st.columns(1)[0]
with row1:
    st.subheader("🧠 AI Market Analysis")
    if st.button("Phân tích thị trường hiện tại"):
        with st.spinner("AI đang phân tích thị trường..."):
            data_context = {
                "global_price": global_price,
                "exchange_rate": exchange_rate,
                "converted_price": converted_price,
                "sjc_price": sjc_data['sell'],
                "gap": gap,
                "news": news
            }
            
            report = get_gold_market_analysis(data_context)
            st.markdown(report)
            
            # Save snapshot with report
            save_snapshot({
                "global_price": global_price,
                "exchange_rate": exchange_rate,
                "sjc_sell": sjc_data['sell'],
                "sjc_buy": sjc_data['buy'],
                "converted_price": converted_price,
                "gap": gap,
                "ai_report": report
            })
            st.success("Báo cáo đã được tạo và lưu trữ trong lịch sử!")

row2 = st.columns(1)[0]
with row2:
    st.subheader("📈 Xu hướng thị trường")
    history_df = get_history(limit=50)
    if not history_df.empty:
        history_df['sjc_sell_million'] = history_df['sjc_sell_price'] / 1_000_000
        
        # Plotly Chart
        fig = px.line(history_df, x='timestamp', y=['sjc_sell_million', 'converted_price'], 
                      labels={'value': 'Giá (Triệu VND/Lượng)', 'timestamp': 'Thời gian', 'variable': 'Loại giá'},
                      title="Giá vàng SJC vs Giá vàng thế giới (Quy đổi sang VND)")
        
        # Rename legend names for clarity
        new_names = {'sjc_sell_million': 'Giá bán SJC', 'converted_price': 'Giá thế giới quy đổi'}
        fig.for_each_trace(lambda t: t.update(name = new_names.get(t.name, t.name)))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu lịch sử. Dữ liệu sẽ được xây dựng khi bạn sử dụng ứng dụng.")

row3 = st.columns(1)[0]
with row3:
    st.subheader("📰 Tin tức thị trường")
    st.markdown(news)
    
# Footer
st.markdown("---")
st.caption("Dữ liệu nguồn: yfinance, Web scraping (SJC). Phân tích bởi OpenRouter LLMs. Đây chỉ là tin tức không phải là lời khuyên tài chính. ^^!")
