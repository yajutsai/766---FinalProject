"""Verify data cleaning results"""

import pandas as pd

df = pd.read_csv('gdelt_data_cleaned.csv')

print('=== Data Cleaning Verification ===')
print(f'Total articles: {len(df)}')
print()

print('1. Date format check:')
print(f'   Sample dates: {df["published_at"].head(3).tolist()}')
date_format_ok = df["published_at"].str.match(r'^\d{4}-\d{2}-\d{2}$').all()
print(f'   Date format consistent (YYYY-MM-DD): {date_format_ok}')
print()

print('2. Language check:')
print(f'   Languages: {df["language"].value_counts().to_dict()}')
all_english = df["language"].str.lower().eq("english").all()
print(f'   All English: {all_english}')
print()

print('3. Title cleaning check:')
print(f'   Sample original: {df["title"].iloc[0]}')
print(f'   Sample cleaned: {df["title_cleaned"].iloc[0]}')
all_lowercase = df["title_cleaned"].str.islower().all()
print(f'   All lowercase: {all_lowercase}')
print()

print('=== Summary ===')
if date_format_ok and all_english and all_lowercase:
    print('[OK] All cleaning requirements met!')
else:
    print('[X] Some requirements not met')
    if not date_format_ok:
        print('  - Date format issue')
    if not all_english:
        print('  - Language filter issue')
    if not all_lowercase:
        print('  - Title lowercase issue')

