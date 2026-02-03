import pandas as pd
import sqlite3
import os
from datetime import datetime

DB_FILE = "gold_data.db"

def init_db():
    """Khởi tạo SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS gold_prices
                 (timestamp TEXT PRIMARY KEY,
                  global_price_usd REAL,
                  exchange_rate REAL,
                  sjc_sell_price REAL,
                  sjc_buy_price REAL,
                  converted_price REAL,
                  gap REAL,
                  ai_report TEXT)''')
    conn.commit()
    conn.close()

def save_snapshot(data):
    """Lưu snapshot dữ liệu vào database."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    try:
        c.execute('''INSERT INTO gold_prices 
                     (timestamp, global_price_usd, exchange_rate, sjc_sell_price, sjc_buy_price, converted_price, gap, ai_report)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (timestamp, 
                   data.get('global_price'), 
                   data.get('exchange_rate'), 
                   data.get('sjc_sell'), 
                   data.get('sjc_buy'), 
                   data.get('converted_price'), 
                   data.get('gap'),
                   data.get('ai_report', "")))
        conn.commit()
    except Exception as e:
        print(f"Error saving to DB: {e}")
    finally:
        conn.close()

def get_history(limit=30):
    """Lấy lịch sử dữ liệu."""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
        
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM gold_prices ORDER BY timestamp DESC LIMIT {limit}", conn)
    conn.close()
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='timestamp', ascending=True)
    
    return df
