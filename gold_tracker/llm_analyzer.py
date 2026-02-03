from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

def get_gold_market_analysis(data_context):
    """
    Tạo báo cáo phân tích thị trường vàng sử dụng OpenRouter LLM.
    
    Args:
        data_context (dict): Dictionary chứa giá vàng, khoảng cách, và tin tức.
    
    Returns:
        str: Báo cáo phân tích thị trường vàng dưới dạng Markdown.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY not found in .env file."

    # Initialize ChatOpenAI with OpenRouter base URL
    # Using a more stable model or allowing fallback
    # Common free/cheap models: google/gemini-2.0-flash-001, mistralai/mistral-7b-instruct:free
    model_name = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    
    llm = ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7
    )

    system_prompt = """
        You are a senior financial expert specializing in the Vietnam gold market. 
        Your goal is to provide a professional, data-driven analysis of the daily gold prices.
        You are analytical, objective, and insightful. You understand the correlation between global XAU/USD, the USD/VND exchange rate, and the local SJC gold price.
        You always format your output in clean Markdown.
    """

    human_prompt = """
    Please generate a daily gold market report based on the following data:

    **Data Snapshot:**
    - Global Gold Price (Spot): ${global_price:.2f}/lượng
    - USD/VND Exchange Rate: {exchange_rate:,.0f} VND
    - Converted Global Price: {converted_price:.2f} Million VND/lượng
    - SJC Gold Price (Sell): {sjc_price_million:.2f} Million VND/lượng
    - Gap (Domestic vs Global): {gap:.2f} Million VND/lượng
    
    **Latest Financial News:**
    {news}

    **Task:**
    Create a structured report including:
    1. **Today's Snapshot**: A clear table of the prices above.
    2. **Market Divergence**: Analyze the 'Gap'. Is it high or low compared to historical norms (normally 2-5 million is acceptable, >10 is high)? What does this imply?
    3. **Expert Prediction**: Give a 'Bullish', 'Bearish', or 'Neutral' forecast for the next 24-48h.
    4. **Reasoning**: Explain why based on the DXY index (implied from news/context), Fed news, or local demand.
    5. **Disclaimer**: A professional financial disclaimer at the end.
    
    Write the report in Vietnamese (or English if requested, but default to Vietnamese for this task).
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    chain = prompt | llm | StrOutputParser()

    # Prepare inputs
    sjc_price = data_context.get('sjc_price', 0)
    sjc_price_million = sjc_price / 1000000 if sjc_price else 0
    
    try:
        result = chain.invoke({
            "global_price": data_context.get('global_price', 0),
            "exchange_rate": data_context.get('exchange_rate', 0),
            "converted_price": data_context.get('converted_price', 0),
            "sjc_price_million": sjc_price_million,
            "gap": data_context.get('gap', 0),
            "news": data_context.get('news', "No specific news available at this moment.")
        })
        return result
    except Exception as e:
        return f"Error generating analysis: {e}"
