# Vietnam Gold Tracker & AI Forecaster

A production-ready Python application that tracks daily gold prices in Vietnam (SJC), compares them with global markets (XAU/USD), and provides expert-level forecasts using LLMs (via OpenRouter).

## Features

- **Real-time Data**: Scrapes SJC gold prices and fetches global spot prices + USD/VND rates.
- **Smart Conversion**: Calculates the parity price and the "Gap" between domestic and international markets.
- **AI Analysis**: Generates professional financial reports with "Bullish/Bearish" predictions using LLMs.
- **Interactive Dashboard**: Built with Streamlit for easy visualization.
- **History Tracking**: Saves data snapshots to a local SQLite database for trend analysis.
- **Dockerized**: Ready for deployment.

## Tech Stack

- **Python 3.10+**
- **Streamlit**: UI Framework
- **LangChain**: AI/LLM Orchestration
- **yfinance**: Global Market Data
- **BeautifulSoup4**: Web Scraping
- **SQLite**: Data Persistence

## Setup & Running

### 1. Local Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables:
    - Create a `.env` file in the root directory.
    - Add your OpenRouter API Key:
      ```env
      OPENROUTER_API_KEY=your_key_here
      ```
4.  Run the Streamlit App:
    ```bash
    streamlit run app.py
    ```

### 2. Docker Deployment

1.  Build the image:
    ```bash
    docker build -t gold-tracker .
    ```
2.  Run the container:
    ```bash
    docker run -p 8501:8501 --env-file .env gold-tracker
    ```
    Access the app at `http://localhost:8501`.

## Project Structure

- `app.py`: Main Streamlit application entry point.
- `main.py`: Legacy CLI entry point.
- `gold_tracker/`: Core logic package.
  - `data_fetcher.py`: Data retrieval logic.
  - `calculator.py`: Financial formulas.
  - `llm_analyzer.py`: LangChain integration.
  - `storage.py`: SQLite database management.

## Disclaimer

This tool is for informational purposes only and does not constitute financial advice.
