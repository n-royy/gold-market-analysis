def calculate_converted_global_price(global_price_usd, exchange_rate):
    """
    Chuyển đổi giá vàng toàn cầu ($/oz) thành giá vàng địa phương (Million VND/lượng).
    Công thức: (GlobalPrice * 1.205 * ExchangeRate) / 1,000,000
    
    Args:
        global_price_usd (float): Giá vàng toàn cầu trong USD/oz.
        exchange_rate (float): Tỷ giá USD/VND.
        
    Returns:
        float: Giá vàng địa phương trong Million VND/lượng.
    """
    if global_price_usd is None or exchange_rate is None:
        return None
    
    local_price = (global_price_usd * exchange_rate) / 1000000
    return local_price

def calculate_gap(sjc_price_vnd, converted_global_price_million_vnd):
    """
    Tính toán khoảng cách giữa giá SJC và giá vàng toàn cầu đã chuyển đổi.
    
    Args:
        sjc_price_vnd (float): Giá SJC trong VND (lượng đầy đủ).
        converted_global_price_million_vnd (float): Giá vàng toàn cầu đã chuyển đổi trong Million VND.
        
    Returns:
        float: Khoảng cách trong Million VND.
    """
    if sjc_price_vnd is None or converted_global_price_million_vnd is None:
        return None
    
    # Convert SJC to Million VND
    sjc_million = sjc_price_vnd / 1000000
    
    gap = sjc_million - converted_global_price_million_vnd
    return gap
