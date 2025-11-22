# News Collection

This folder contains all scripts and data files related to news data collection and processing.

## Files

### Scripts

- **`fetch_gdelt_data.py`** - Main script to fetch news articles from GDELT API
  - Fetches cryptocurrency-related news (bitcoin, btc, ethereum, eth, etc.)
  - Date range: 2024/11/1 - 2025/11/1
  - Outputs: `gdelt_data.json` and `gdelt_data.csv`

- **`clean_gdelt_data.py`** - Data cleaning script
  - Standardizes date format to YYYY-MM-DD
  - Filters to English articles only
  - Cleans titles (lowercase, symbol processing)
  - Outputs: `gdelt_data_cleaned.json` and `gdelt_data_cleaned.csv`

- **`verify_cleaning.py`** - Verification script to check data quality
  - Verifies date format consistency
  - Checks language filter
  - Validates title cleaning

- **`test_gdelt_api.py`** - Test script for GDELT API connectivity

- **`fetch_cryptopanic_data.py`** - Legacy script for CryptoPanic API (has data limitations)

### Data Files

- **`gdelt_data.json`** - Raw JSON data from GDELT API
- **`gdelt_data.csv`** - Raw CSV data from GDELT API
- **`gdelt_data_cleaned.json`** - Cleaned JSON data
- **`gdelt_data_cleaned.csv`** - Cleaned CSV data (ready for analysis)

## Usage

### Fetch Data
```bash
cd news_collection
python fetch_gdelt_data.py
```

### Clean Data
```bash
cd news_collection
python clean_gdelt_data.py
```

### Verify Cleaning
```bash
cd news_collection
python verify_cleaning.py
```

## Data Statistics

- **Total Articles**: 2,466 (after cleaning)
- **Date Range**: 2024-11-01 to 2025-10-31
- **Language**: English only
- **Unique Sources**: 339
- **Keywords**: bitcoin, btc, ethereum, eth, cryptocurrency, crypto, blockchain, digital currency

