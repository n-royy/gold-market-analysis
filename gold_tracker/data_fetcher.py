import requests
from bs4 import BeautifulSoup
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

def get_global_gold_price():
    """
    Lấy giá vàng quốc tế (XAU/USD) sử dụng yfinance.
    Returns:
        float: Giá vàng trong đô la США mỗi ounce.
    """
    try:
        # GC=F là Futures của vàng, đây là một proxy tốt cho giá spot.
        # Hoặc có thể tìm ticker tốt hơn nếu cần.
        ticker = yf.Ticker("GC=F")
        rateOzToVN = 1.20565
        # Lấy giá mới nhất
        data = ticker.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            return price * rateOzToVN
        else:
            logger.error("Không có dữ liệu cho GC=F")
            return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def get_usd_vnd_rate():
    """
    Lấy tỷ giá USD/VND sử dụng yfinance.
    Returns:
        float: Tỷ giá (VND mỗi USD).
    """
    try:
        ticker = yf.Ticker("VND=X")
        data = ticker.history(period="1d")
        if not data.empty:
            rate = data['Close'].iloc[-1]
            return rate
        else:
            logger.error("Không có dữ liệu cho VND=X")
            return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def get_sjc_gold_price():
    """
    Lấy giá vàng tại SJC từ webgia.com.
    Returns:
        dict: {'buy': float, 'sell': float} trong VND/lượng (thường là triệu VND, nhưng chúng ta sẽ chuẩn hóa).
    """
    url = "https://webgia.com/gia-vang/sjc/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Tìm bảng chứa "SJC"
            # Cấu trúc trang web thường có bảng với các thành phố.
            # Chúng ta muốn giá vàng tiêu chuẩn tại SJC (thường là hàng đầu hoặc HCM).
            
            # Phương pháp đơn giản: Tìm tất cả các bảng, tìm bảng có "Mua vào"
            tables = soup.find_all('table')
            for table in tables:
                if "Mua" in table.text and "Bán" in table.text:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        # Tìm hàng chứa giá vàng tiêu chuẩn tại SJC, thường là hàng đầu tiên hoặc HCM
                        # Dòng này có thể có dạng "SJC 1L - 10L" hoặc chỉ "SJC"
                        # Để đơn giản, chúng ta lấy hàng đầu tiên có giá trị hợp lệ sau tiêu đề
                        if len(cols) >= 3:
                            # Dòng có dạng: Loại | Mua | Bán
                            try:
                                buy_text = cols[1].text.strip().replace('.', '').replace(',', '.')
                                sell_text = cols[2].text.strip().replace('.', '').replace(',', '.')
                                
                                # Convert to float
                                buy_price = float(buy_text)
                                sell_price = float(sell_text)
                                
                                # Webgia thường hiển thị giá vàng trong '000 VND hoặc Million. 
                                # Chúng ta sẽ kiểm tra mức độ. Nếu gần 70-90, nó là million. 
                                # Nếu gần 70000, nó là thousand.
                                # Giá vàng hiện tại thường là 80-90 million VND / lượng.
                                
                                # Nếu giá trị được phân tích lớn hơn 1,000,000, nó có thể là VND thô.
                                # Nếu gần 80,000, nó có thể là '000 VND.
                                # Nếu gần 80, nó có thể là million.
                                
                                # Chúng ta sẽ chuẩn hóa tất cả về VND (full units).
                                # Nhưng webgia có thể hiển thị "80,000" có nghĩa là 80,000,000? Không, thường "80,000" có nghĩa là 80,000,000 nếu đơn vị là '000.
                                # Chúng ta sẽ giả sử trang web sử dụng đơn vị '000.
                                # Ví dụ: 80,000 -> 80,000,000.
                                
                                # Nếu phân tích không chắc chắn, chúng ta có thể cần xác nhận thủ công.
                                # Nhưng thường webgia hiển thị giá vàng trong '000 VND hoặc Million. 
                                # Chúng ta sẽ giả sử nó là '000 VND.
                                # Ví dụ: 80,000 -> 80,000,000.
                                
                                if buy_price < 1000: # Million (e.g. 80.5)
                                    buy_price *= 1000000
                                    sell_price *= 1000000
                                elif buy_price < 1000000: # Thousand (e.g. 80500)
                                    buy_price *= 1000
                                    sell_price *= 1000
                                
                                # Heuristic check for unit (Chỉ vs Lượng/lượng)
                                # Nếu giá trị nằm trong khoảng 5M - 40M, và năm hiện tại > 2024, có thể là per Chỉ (3.75g)
                                # Giá vàng > 70M/lượng kể từ năm 2024.
                                # Vì vậy, nếu thấy giá ~17M, có thể là per Chỉ.
                                # Chúng ta muốn VND/lượng.
                                if 5000000 < sell_price < 50000000:
                                    buy_price *= 10
                                    sell_price *= 10
                                
                                return {'buy': buy_price, 'sell': sell_price}
                            except ValueError:
                                continue
    except Exception as e:
        logger.error(f"Error scraping SJC price: {e}")
    
    return None

def fetch_gold_news():
    """
    Lấy tin tức vàng/kinh tế mới nhất từ VnExpress hoặc nguồn tương tự.
    Returns:
        str: Một chuỗi chứa các điểm tin tức vàng/kinh tế.
    """
    url = "https://vnexpress.net/kinh-doanh/hang-hoa"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find news titles. VnExpress usually uses h3.title-news a
            articles = soup.find_all('h2', class_='title-news')
            headlines = []
            for article in articles[:10]: # Top 10 news
                a_tag = article.find('a')
                if a_tag:
                    title = a_tag.get('title') or a_tag.text.strip()
                    link = a_tag.get('href')
                    # Đảm bảo link luôn có domain đầy đủ
                    if link and link.startswith('/'):
                        link = "https://vnexpress.net" + link
                    headlines.append(f"- {title} ({link})")
            
            if headlines:
                return "\n".join(headlines)
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        
    return "Không có tin tức vàng/kinh tế mới nhất được lấy. Vui lòng kiểm tra tin tức thị trường thủ công."
