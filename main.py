import argparse
import sys
import os
from dotenv import load_dotenv
from gold_tracker.data_fetcher import get_global_gold_price, get_usd_vnd_rate, get_sjc_gold_price, fetch_gold_news
from gold_tracker.calculator import calculate_converted_global_price, calculate_gap
from gold_tracker.llm_analyzer import get_gold_market_analysis
from gold_tracker.storage import save_snapshot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Vietnam Gold Price Tracker & AI Forecaster")
    parser.add_argument("--mock", action="store_true", help="Use mock data for testing")
    args = parser.parse_args()

    load_dotenv()
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or "your_openrouter_api_key_here" in api_key:
        print("⚠️  WARNING: OPENROUTER_API_KEY not found or invalid in .env file.")
        print("   AI Analysis will fail. Please set your API key in .env.")
        print("   Get a key from: https://openrouter.ai/keys\n")

    print("🚀 Starting Gold Tracker App...\n")

    # 1. Fetch Data
    print("Fetching data...")
    if args.mock:
        global_price = 2030.50
        exchange_rate = 24500
        sjc_data = {'buy': 78000000, 'sell': 80000000}
        news = "- Gold prices hit record high.\n- Fed likely to cut rates."
        print("Using MOCK data.")
    else:
        global_price = get_global_gold_price()
        exchange_rate = get_usd_vnd_rate()
        sjc_data = get_sjc_gold_price()
        news = fetch_gold_news()

    # Handle missing data
    if global_price is None:
        print("❌ Failed to fetch Global Gold Price. Using fallback (2600 USD/oz).")
        global_price = 2600.0 # Approximate current price
    else:
        print(f"✅ Giá vàng quốc tế: ${global_price:.2f}/lượng")

    if exchange_rate is None:
        print("❌ Failed to fetch USD/VND Rate. Using fallback (25,400 VND).")
        exchange_rate = 25400.0
    else:
        print(f"✅ USD/VND Rate: {exchange_rate:,.0f} VND")

    if sjc_data is None:
        print("❌ Failed to fetch SJC Price. Using fallback (Sell: 85,000,000 VND).")
        sjc_data = {'buy': 83000000, 'sell': 85000000}
    else:
        print(f"✅ Giá vàng bán ra của SJC: {sjc_data['sell']:,.0f} VND/lượng")

    # 2. Calculate
    converted_price = calculate_converted_global_price(global_price, exchange_rate)
    gap = calculate_gap(sjc_data['sell'], converted_price)

    print(f"📊 Quy đổi giá vàng thế giới sang tiền Việt: {converted_price:.2f} Triệu VND/lượng")
    print(f"📉 Chênh lệnh: {gap:.2f} Triệu VND/lượng")
    
    # 3. AI Analysis
    print("\n🧠 Generating AI Analysis (this may take a few seconds)...")
    
    data_context = {
        "global_price": global_price,
        "exchange_rate": exchange_rate,
        "converted_price": converted_price,
        "sjc_price": sjc_data['sell'],
        "gap": gap,
        "news": news
    }

    report = get_gold_market_analysis(data_context)
    
    print("\n" + "="*50)
    print("       GOLD MARKET INTELLIGENCE REPORT       ")
    print("="*50 + "\n")
    print(report)
    print("\n" + "="*50)

    # 4. Save to DB
    print("💾 Saving snapshot to database...")
    save_snapshot({
        "global_price": global_price,
        "exchange_rate": exchange_rate,
        "sjc_sell": sjc_data['sell'],
        "sjc_buy": sjc_data['buy'],
        "converted_price": converted_price,
        "gap": gap,
        "ai_report": report
    })
    print("✅ Data saved.")

if __name__ == "__main__":
    main()
