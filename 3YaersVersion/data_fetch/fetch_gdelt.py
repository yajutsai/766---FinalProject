"""
GDELT Data Fetcher
Fetches news articles from GDELT API for cryptocurrency-related keywords
Date range: 2024/11/1 - 2025/11/1
Keywords: bitcoin, btc, ethereum, eth, cryptocurrency, crypto, blockchain, digital currency
"""

import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from urllib.parse import quote

# GDELT API configuration
BASE_URL = 'https://api.gdeltproject.org/api/v2/doc/doc'

# Keywords to search for
KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", 
    "cryptocurrency", "crypto", "blockchain", "digital currency"
]

# Date range
START_DATE = '2022-11-01'
END_DATE = '2025-11-01'

# Maximum records per request (GDELT limit is usually 250)
MAX_RECORDS_PER_REQUEST = 250


def build_query_string(keywords):
    """Build OR query string for GDELT API (must be wrapped in parentheses)"""
    query = ' OR '.join(keywords)
    return f'({query})'


def format_datetime_for_gdelt(date_str):
    """Convert date string (YYYY-MM-DD) to GDELT format (YYYYMMDDHHMMSS)"""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%Y%m%d000000')


def fetch_gdelt_data(start_date, end_date, keywords, max_records=5000):
    """
    Fetch data from GDELT API
    Splits large date ranges into monthly chunks to avoid API limits
    
    Args:
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        keywords: List of keywords to search for
        max_records: Maximum number of records to fetch
    
    Returns:
        List of articles
    """
    all_articles = []
    query = build_query_string(keywords)
    
    print(f"Fetching GDELT data from {start_date} to {end_date}")
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Query: {query}")
    print()
    
    # Split date range into monthly chunks to avoid API limits
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Generate monthly date ranges
    date_ranges = []
    current = start_dt
    while current < end_dt:
        # Calculate end of current month or end_date, whichever is earlier
        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1, day=1)
        else:
            next_month = current.replace(month=current.month + 1, day=1)
        
        range_end = min(next_month - timedelta(days=1), end_dt)
        date_ranges.append((
            current.strftime('%Y-%m-%d'),
            range_end.strftime('%Y-%m-%d')
        ))
        current = next_month
    
    print(f"Split into {len(date_ranges)} monthly chunks")
    print()
    
    # Fetch data for each date range
    for i, (range_start, range_end) in enumerate(date_ranges, 1):
        print(f"Fetching chunk {i}/{len(date_ranges)}: {range_start} to {range_end}")
        
        # Format dates for GDELT API
        start_datetime = format_datetime_for_gdelt(range_start)
        end_datetime = format_datetime_for_gdelt(range_end)
        
        # GDELT API parameters
        params = {
            'query': query,
            'mode': 'artlist',
            'maxrecords': MAX_RECORDS_PER_REQUEST,
            'format': 'json',
            'startdatetime': start_datetime,
            'enddatetime': end_datetime
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=60)
            
            if response.status_code != 200:
                print(f"  Error: HTTP {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                continue
            
            # GDELT API returns JSON with 'articles' key
            content = response.text.strip()
            
            # Parse JSON
            try:
                data = json.loads(content)
                
                # GDELT returns data in format: {"articles": [...]}
                if isinstance(data, dict) and 'articles' in data:
                    articles = data['articles']
                elif isinstance(data, list):
                    articles = data
                else:
                    print(f"  Unexpected response format")
                    articles = []
                    
            except json.JSONDecodeError as e:
                print(f"  Error parsing JSON: {e}")
                continue
            
            print(f"  Fetched {len(articles)} articles")
            
            # Filter articles to ensure they're relevant
            filtered_articles = filter_relevant_articles(articles, keywords)
            print(f"  After filtering: {len(filtered_articles)} relevant articles")
            
            all_articles.extend(filtered_articles)
            
            # Rate limiting
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching data: {e}")
            continue
        except Exception as e:
            print(f"  Unexpected error: {e}")
            continue
    
    print(f"\nTotal articles fetched: {len(all_articles)}")
    return all_articles


def filter_relevant_articles(articles, keywords):
    """
    Filter articles to keep only those relevant to cryptocurrency
    Remove articles that are clearly not about cryptocurrency
    
    Args:
        articles: List of article dictionaries
        keywords: List of keywords to check for
    
    Returns:
        Filtered list of articles
    """
    filtered = []
    keyword_pattern = re.compile(
        r'\b(bitcoin|btc|ethereum|eth|cryptocurrency|crypto|blockchain|digital\s+currency)\b',
        re.IGNORECASE
    )
    
    # Patterns to exclude (articles that mention keywords but are not about crypto)
    exclude_patterns = [
        r'\b(energy|power|electricity|mining)\s+(bitcoin|btc)\b',  # Energy mining, not crypto
        r'\b(bitcoin|btc)\s+(mining|energy)',  # Bitcoin energy/mining (non-crypto context)
    ]
    exclude_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in exclude_patterns]
    
    for article in articles:
        # Get article text
        title = article.get('title', '') or ''
        snippet = article.get('snippet', '') or ''
        url = article.get('url', '') or ''
        text = f"{title} {snippet} {url}".lower()
        
        # Must contain at least one keyword
        if not keyword_pattern.search(text):
            continue
        
        # Exclude if matches exclusion patterns
        should_exclude = False
        for exclude_pattern in exclude_compiled:
            if exclude_pattern.search(text):
                should_exclude = True
                break
        
        if not should_exclude:
            filtered.append(article)
    
    return filtered


def process_and_export_data(articles, output_file='gdelt_data.json'):
    """
    Process articles and export to JSON and CSV files
    
    Args:
        articles: List of article dictionaries
        output_file: Base name for output files
    """
    if not articles:
        print("No articles to export")
        return
    
    # Export raw JSON
    json_file = output_file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"\nExported {len(articles)} articles to {json_file}")
    
    # Process into DataFrame for CSV export
    processed_data = []
    for article in articles:
        # GDELT article structure
        # Parse seendate format: 20241109T164500Z
        seendate = article.get('seendate', '')
        formatted_date = ''
        if seendate:
            try:
                # Parse GDELT date format: YYYYMMDDTHHMMSSZ
                dt = datetime.strptime(seendate, '%Y%m%dT%H%M%SZ')
                formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_date = seendate
        
        processed_data.append({
            'title': article.get('title', ''),
            'url': article.get('url', ''),
            'published_at': formatted_date,
            'seendate': seendate,
            'source': article.get('domain', '') or article.get('source', ''),
            'snippet': article.get('snippet', ''),
            'language': article.get('language', 'unknown'),
        })
    
    df = pd.DataFrame(processed_data)
    
    # Remove duplicates based on URL
    df = df.drop_duplicates(subset=['url'], keep='first')
    
    # Export to CSV
    csv_file = output_file.replace('.json', '.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"Exported processed data to {csv_file} (after removing duplicates: {len(df)} articles)")
    
    # Print summary statistics
    print(f"\n=== Data Summary ===")
    print(f"Total articles: {len(articles)}")
    print(f"Unique articles: {len(df)}")
    if 'published_at' in df.columns and len(df) > 0:
        dates = df['published_at'].dropna()
        if len(dates) > 0:
            print(f"Date range: {dates.min()} to {dates.max()}")
    print(f"Unique sources: {df['source'].nunique()}")
    print(f"Languages: {df['language'].value_counts().to_dict()}")


def main():
    """Main function to fetch and export GDELT data"""
    
    print("=" * 60)
    print("GDELT Data Fetcher")
    print("=" * 60)
    print()
    
    # Fetch data
    articles = fetch_gdelt_data(START_DATE, END_DATE, KEYWORDS, max_records=5000)
    
    if articles:
        # Export data
        process_and_export_data(articles, 'gdelt_data.json')
        print("\n[SUCCESS] Data fetching and export completed successfully!")
    else:
        print("\n[ERROR] No articles were fetched.")
        print("\nPossible reasons:")
        print("  1. No articles match the keywords in the date range")
        print("  2. GDELT API may have rate limiting")
        print("  3. Date range might need adjustment")
        print("\nTry:")
        print("  - Checking GDELT API status")
        print("  - Adjusting the date range")
        print("  - Verifying keywords are correct")


if __name__ == '__main__':
    main()

