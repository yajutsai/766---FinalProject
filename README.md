# GDELT Data Fetcher

This script fetches news articles from GDELT API for cryptocurrency-related keywords (Bitcoin, BTC, Ethereum, ETH, cryptocurrency, crypto, blockchain, digital currency).

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Navigate to news collection folder:**
   ```bash
   cd news_collection
   ```

3. **Run the script:**
   ```bash
   python fetch_gdelt_data.py
   ```

   **Note:** GDELT API is free and doesn't require an API key!

## Project Structure

```
.
├── news_collection/          # News data collection and processing
│   ├── fetch_gdelt_data.py   # Main data fetching script
│   ├── clean_gdelt_data.py   # Data cleaning script
│   ├── verify_cleaning.py     # Data verification script
│   ├── gdelt_data.json       # Raw data (JSON)
│   ├── gdelt_data.csv        # Raw data (CSV)
│   ├── gdelt_data_cleaned.json  # Cleaned data (JSON)
│   └── gdelt_data_cleaned.csv  # Cleaned data (CSV)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Output

The script will generate two files in `news_collection/` folder:
- `gdelt_data.json`: Raw JSON data from the API
- `gdelt_data.csv`: Processed data in CSV format (duplicates removed)

## Data Cleaning

After fetching data, run the cleaning script:
```bash
cd news_collection
python clean_gdelt_data.py
```

This will create cleaned versions:
- `gdelt_data_cleaned.json`: Cleaned JSON data
- `gdelt_data_cleaned.csv`: Cleaned CSV data

**Cleaning steps:**
1. Standardize date format to YYYY-MM-DD
2. Keep only English articles
3. Clean titles (convert to lowercase, handle symbols)

## Configuration

The script is configured to fetch data:
- **Date range**: 2024/11/1 to 2025/11/1
- **Keywords**: bitcoin, btc, ethereum, eth, cryptocurrency, crypto, blockchain, digital currency

You can modify these settings in `news_collection/fetch_gdelt_data.py`:
- `START_DATE`: Start date in 'YYYY-MM-DD' format
- `END_DATE`: End date in 'YYYY-MM-DD' format
- `KEYWORDS`: List of keywords to search for

## Features

- Automatically splits large date ranges into monthly chunks
- Filters articles to keep only relevant cryptocurrency content
- Removes duplicate articles based on URL
- Exports to both JSON and CSV formats

## Legacy Scripts

- `fetch_cryptopanic_data.py`: Original CryptoPanic API fetcher (has data limitations)
- `test_api.py`, `test_gdelt_api.py`: Testing scripts for API connectivity

