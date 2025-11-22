"""
CryptoPanic Data Fetcher
Fetches news headlines and sentiment data from CryptoPanic API
for BTC and ETH from 2024/11/1 to 2025/11/1
"""

import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# CryptoPanic API configuration
API_KEY = os.getenv('CRYPTOPANIC_API_KEY')
# Try different possible API endpoints
BASE_URL = 'https://cryptopanic.com/api/v1/posts/'

if not API_KEY:
    raise ValueError("CRYPTOPANIC_API_KEY not found in environment variables. Please create a .env file with your API key.")


def fetch_cryptopanic_data(start_date, end_date, currencies, api_key):
    """
    Fetch data from CryptoPanic API for specified date range and currencies
    
    Args:
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        currencies: Comma-separated string of currencies (e.g., 'BTC,ETH')
        api_key: CryptoPanic API key
    
    Returns:
        List of all posts/headlines
    """
    all_posts = []
    page = 1
    
    # Convert dates to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    print(f"Fetching data from {start_date} to {end_date} for currencies: {currencies}")
    print(f"API Key: {api_key[:10]}..." if api_key else "No API Key")
    
    max_pages = 50  # Limit to prevent infinite loops
    pages_with_no_results = 0  # Track consecutive pages with no results
    
    while page <= max_pages:
        # CryptoPanic API parameters
        # Note: API doesn't seem to support date filtering, so we'll filter client-side
        params = {
            'auth_token': api_key,
            'currencies': currencies,
            'page': page,
            'public': 'true'
        }
        
        try:
            print(f"\n[DEBUG] Request URL: {BASE_URL}")
            print(f"[DEBUG] Request params: {dict((k, v if k != 'auth_token' else '***') for k, v in params.items())}")
            
            response = requests.get(BASE_URL, params=params, timeout=30)
            
            print(f"[DEBUG] Response status code: {response.status_code}")
            
            # Check if response is successful
            if response.status_code != 200:
                print(f"[DEBUG] Response text: {response.text[:500]}")
                response.raise_for_status()
            
            data = response.json()
            
            print(f"[DEBUG] Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            print(f"[DEBUG] Full response (first 500 chars): {str(data)[:500]}")
            
            # Check different possible response formats
            posts = []
            if 'results' in data:
                posts = data['results']
            elif isinstance(data, list):
                posts = data
            elif 'data' in data:
                posts = data['data']
            
            print(f"[DEBUG] Found {len(posts)} posts in response")
            
            if len(posts) == 0:
                print(f"No more results at page {page}")
                if page == 1:
                    print("[DEBUG] First page returned no results. Check API key and parameters.")
                break
            
            # Filter posts by date range
            filtered_posts = []
            for i, post in enumerate(posts):
                # Try different date field names (prefer published_at)
                post_date_str = post.get('published_at') or post.get('created_at') or post.get('date')
                
                if post_date_str:
                    try:
                        # Handle ISO format dates (e.g., "2025-11-21T04:37:40Z" or "2025-11-21T04:37:40+00:00")
                        if isinstance(post_date_str, str):
                            # Parse ISO format with timezone
                            if post_date_str.endswith('Z'):
                                # Replace Z with +00:00 for fromisoformat
                                post_date_str_clean = post_date_str.replace('Z', '+00:00')
                            else:
                                post_date_str_clean = post_date_str
                            
                            try:
                                post_date = datetime.fromisoformat(post_date_str_clean)
                            except ValueError:
                                # Try without timezone
                                post_date_str_clean = post_date_str.replace('Z', '').replace('+00:00', '')
                                try:
                                    post_date = datetime.fromisoformat(post_date_str_clean)
                                except:
                                    # Try other formats
                                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                                        try:
                                            post_date = datetime.strptime(post_date_str_clean[:19], fmt)
                                            break
                                        except:
                                            continue
                                    else:
                                        raise ValueError(f"Could not parse date: {post_date_str}")
                            
                            # Convert to naive datetime for comparison
                            if post_date.tzinfo is not None:
                                post_date_naive = post_date.replace(tzinfo=None)
                            else:
                                post_date_naive = post_date
                            
                            # Debug first few posts
                            if i < 3:
                                print(f"[DEBUG] Post {i+1}: date={post_date_naive}, title={post.get('title', '')[:50]}")
                            
                            # Check if date is in range
                            if start_dt <= post_date_naive <= end_dt:
                                filtered_posts.append(post)
                            elif post_date_naive < start_dt:
                                # If we've gone past the start date, we can stop
                                print(f"Reached posts before start date ({post_date_naive}). Stopping at page {page}")
                                return all_posts
                            # If post_date_naive > end_dt, we continue (might be sorting issue)
                        else:
                            # If date is not a string, skip for now
                            if i < 3:
                                print(f"[DEBUG] Post {i+1} has non-string date: {post_date_str} (type: {type(post_date_str)})")
                    except Exception as e:
                        if i < 3:
                            print(f"[DEBUG] Error parsing date {post_date_str}: {e}")
                else:
                    # If no date field, skip
                    if i < 3:
                        print(f"[DEBUG] Post {i+1} has no date field. Keys: {list(post.keys())}")
            
            all_posts.extend(filtered_posts)
            print(f"Page {page}: Found {len(filtered_posts)} posts in date range (Total: {len(all_posts)})")
            
            # Check if we've gone too far back (all posts are before start date)
            if len(filtered_posts) == 0 and len(posts) > 0:
                # Check if all posts in this page are before start date
                all_before_start = True
                for post in posts:
                    post_date_str = post.get('published_at') or post.get('created_at')
                    if post_date_str:
                        try:
                            if post_date_str.endswith('Z'):
                                post_date_str_clean = post_date_str.replace('Z', '+00:00')
                            else:
                                post_date_str_clean = post_date_str
                            post_date = datetime.fromisoformat(post_date_str_clean)
                            if post_date.tzinfo:
                                post_date = post_date.replace(tzinfo=None)
                            if post_date >= start_dt:
                                all_before_start = False
                                break
                        except:
                            pass
                
                if all_before_start:
                    print(f"All posts on page {page} are before start date. Stopping.")
                    break
            
            # Check if we have next page
            # Note: CryptoPanic API may return null for next even if more pages exist
            # We'll try a few more pages manually if we haven't found data yet
            has_next = data.get('next') is not None
            
            if not has_next:
                # If we found some data, stop
                if len(all_posts) > 0:
                    print(f"No more pages available (next={data.get('next')})")
                    break
                # If no data found yet, try a few more pages manually
                elif page < 5:
                    print(f"API returned next=null, but trying page {page + 1} manually...")
                else:
                    # After trying 5 pages with no results, give up
                    if len(all_posts) == 0:
                        print(f"\n[WARNING] No data found in date range after {page} pages.")
                        if posts:
                            first_date = posts[0].get('published_at', 'N/A')
                            last_date = posts[-1].get('published_at', 'N/A')
                            print(f"[WARNING] API returned dates: {first_date} to {last_date}")
                            print(f"[WARNING] Requested range: {start_date} to {end_date}")
                            print(f"[WARNING] This might mean:")
                            print(f"  1. API only returns recent data (free tier limitation)")
                            print(f"  2. No data exists in the specified date range")
                            print(f"  3. Date range might need adjustment")
                    print(f"Stopping after {page} pages.")
                    break
            
            page += 1
            
            # Safety limit: stop after 50 pages to avoid infinite loops
            if page > 50:
                print(f"Reached page limit (50). Stopping.")
                break
            
            # Rate limiting - be respectful to the API
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    return all_posts


def process_and_export_data(posts, output_file='cryptopanic_data.json'):
    """
    Process posts and export to JSON and CSV files
    
    Args:
        posts: List of post dictionaries
        output_file: Base name for output files
    """
    if not posts:
        print("No posts to export")
        return
    
    # Export raw JSON
    json_file = output_file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    print(f"\nExported {len(posts)} posts to {json_file}")
    
    # Process into DataFrame for CSV export
    processed_data = []
    for post in posts:
        processed_data.append({
            'id': post.get('id'),
            'title': post.get('title'),
            'url': post.get('url'),
            'published_at': post.get('created_at'),
            'source': post.get('source', {}).get('title', ''),
            'votes': post.get('votes', {}).get('positive', 0) - post.get('votes', {}).get('negative', 0),
            'positive_votes': post.get('votes', {}).get('positive', 0),
            'negative_votes': post.get('votes', {}).get('negative', 0),
            'comments_count': post.get('comments_count', 0),
            'currencies': ', '.join([c.get('code', '') for c in post.get('currencies', [])]),
            'kind': post.get('kind', '')
        })
    
    df = pd.DataFrame(processed_data)
    
    # Export to CSV
    csv_file = output_file.replace('.json', '.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"Exported processed data to {csv_file}")
    
    # Print summary statistics
    print(f"\n=== Data Summary ===")
    print(f"Total posts: {len(posts)}")
    print(f"Date range: {df['published_at'].min()} to {df['published_at'].max()}")
    print(f"Unique sources: {df['source'].nunique()}")
    print(f"Average votes: {df['votes'].mean():.2f}")
    print(f"Total positive votes: {df['positive_votes'].sum()}")
    print(f"Total negative votes: {df['negative_votes'].sum()}")


def main():
    """Main function to fetch and export CryptoPanic data"""
    
    # Configuration
    start_date = '2024-11-01'
    end_date = '2025-11-01'
    currencies = 'BTC,ETH'
    output_file = 'cryptopanic_data.json'
    
    print("=" * 60)
    print("CryptoPanic Data Fetcher")
    print("=" * 60)
    print(f"\nNote: CryptoPanic API may have limitations on historical data access.")
    print(f"Free tier may only return recent posts. If no data is found,")
    print(f"you may need to adjust the date range or check your API plan.\n")
    
    # Fetch data
    posts = fetch_cryptopanic_data(start_date, end_date, currencies, API_KEY)
    
    if posts:
        # Export data
        process_and_export_data(posts, output_file)
        print("\n[SUCCESS] Data fetching and export completed successfully!")
    else:
        print("\n[ERROR] No data was fetched in the specified date range.")
        print("\nPossible reasons:")
        print("  1. API only returns recent data (free tier limitation)")
        print("  2. No posts exist in the specified date range")
        print("  3. Date range needs adjustment")
        print("\nTry:")
        print("  - Using a more recent date range")
        print("  - Checking if your API plan supports historical data")
        print("  - Running test_api.py to see what dates are available")


if __name__ == '__main__':
    main()

