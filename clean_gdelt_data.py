"""
GDELT Data Cleaning Script
Cleans the fetched GDELT data:
1. Standardize date format to YYYY-MM-DD
2. Keep only English articles
3. Clean titles (lowercase, simple symbol processing)
"""

import pandas as pd
import re
from datetime import datetime

INPUT_JSON = 'gdelt_data.json'
INPUT_CSV = 'gdelt_data.csv'
OUTPUT_JSON = 'gdelt_data_cleaned.json'
OUTPUT_CSV = 'gdelt_data_cleaned.csv'


def clean_title(title):
    """
    Clean title: convert to lowercase and handle simple symbols
    
    Args:
        title: Original title string
    
    Returns:
        Cleaned title string
    """
    if pd.isna(title) or not isinstance(title, str):
        return ''
    
    # Convert to lowercase
    title = title.lower()
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    # Handle common symbol issues (optional - can be customized)
    # Remove multiple spaces
    title = re.sub(r'\s+', ' ', title)
    
    return title.strip()


def standardize_date(date_str):
    """
    Standardize date format to YYYY-MM-DD
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        Date string in YYYY-MM-DD format, or empty string if invalid
    """
    if pd.isna(date_str) or not isinstance(date_str, str):
        return ''
    
    # Try different date formats
    date_formats = [
        '%Y-%m-%d %H:%M:%S',  # 2024-11-01 08:00:00
        '%Y-%m-%d',           # 2024-11-01
        '%Y%m%dT%H%M%SZ',     # 20241118T080000Z (GDELT format)
        '%Y-%m-%dT%H:%M:%SZ', # ISO format
        '%Y-%m-%dT%H:%M:%S',  # ISO without Z
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            continue
    
    # If all formats fail, try to extract date-like pattern
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if date_match:
        return date_match.group(0)
    
    # Return empty string if can't parse
    return ''


def clean_data(df):
    """
    Clean the dataframe
    
    Args:
        df: Input dataframe
    
    Returns:
        Cleaned dataframe
    """
    print(f"Original data: {len(df)} rows")
    
    # 1. Keep only English articles
    if 'language' in df.columns:
        df = df[df['language'].str.lower() == 'english'].copy()
        print(f"After language filter (English only): {len(df)} rows")
    else:
        print("Warning: 'language' column not found, skipping language filter")
    
    # 2. Standardize date format
    if 'published_at' in df.columns:
        df['published_at'] = df['published_at'].apply(standardize_date)
        # Remove rows with invalid dates
        df = df[df['published_at'] != ''].copy()
        print(f"After date standardization: {len(df)} rows")
    
    # Also standardize seendate if it exists
    if 'seendate' in df.columns:
        df['seendate_standardized'] = df['seendate'].apply(standardize_date)
    
    # 3. Clean titles
    if 'title' in df.columns:
        df['title_cleaned'] = df['title'].apply(clean_title)
        # Keep original title for reference, but add cleaned version
        print(f"Titles cleaned: {df['title'].notna().sum()} titles processed")
    
    # Remove rows with empty titles
    if 'title_cleaned' in df.columns:
        df = df[df['title_cleaned'] != ''].copy()
        print(f"After removing empty titles: {len(df)} rows")
    
    # Sort by date
    if 'published_at' in df.columns:
        df = df.sort_values('published_at').reset_index(drop=True)
    
    return df


def main():
    """Main function to clean GDELT data"""
    
    print("=" * 60)
    print("GDELT Data Cleaning")
    print("=" * 60)
    print()
    
    # Try to load from CSV first (faster), fall back to JSON
    try:
        print(f"Loading data from {INPUT_CSV}...")
        df = pd.read_csv(INPUT_CSV)
        print(f"Loaded {len(df)} rows")
    except FileNotFoundError:
        print(f"{INPUT_CSV} not found, trying {INPUT_JSON}...")
        try:
            import json
            with open(INPUT_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            print(f"Loaded {len(df)} rows from JSON")
        except FileNotFoundError:
            print(f"Error: Neither {INPUT_CSV} nor {INPUT_JSON} found!")
            return
    
    print(f"\nOriginal columns: {list(df.columns)}")
    print()
    
    # Clean data
    df_cleaned = clean_data(df)
    
    # Reorder columns for better readability
    column_order = ['published_at', 'title_cleaned', 'title', 'url', 'source', 'snippet', 'language']
    # Add any other columns that exist
    other_columns = [col for col in df_cleaned.columns if col not in column_order]
    final_columns = [col for col in column_order if col in df_cleaned.columns] + other_columns
    df_cleaned = df_cleaned[final_columns]
    
    # Save cleaned data
    print(f"\nSaving cleaned data...")
    
    # Save as CSV
    df_cleaned.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    print(f"Saved to {OUTPUT_CSV}")
    
    # Save as JSON
    df_cleaned.to_json(OUTPUT_JSON, orient='records', indent=2, force_ascii=False)
    print(f"Saved to {OUTPUT_JSON}")
    
    # Print summary
    print(f"\n=== Cleaning Summary ===")
    print(f"Original rows: {len(df)}")
    print(f"Cleaned rows: {len(df_cleaned)}")
    print(f"Removed rows: {len(df) - len(df_cleaned)}")
    
    if 'published_at' in df_cleaned.columns:
        dates = df_cleaned['published_at'].dropna()
        if len(dates) > 0:
            print(f"Date range: {dates.min()} to {dates.max()}")
    
    if 'source' in df_cleaned.columns:
        print(f"Unique sources: {df_cleaned['source'].nunique()}")
    
    print(f"\n[SUCCESS] Data cleaning completed!")
    print(f"\nCleaned files:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_JSON}")


if __name__ == '__main__':
    main()

