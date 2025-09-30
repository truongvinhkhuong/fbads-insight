#!/usr/bin/env python3

import os
import requests

def main():
    base = os.environ.get('TEST_BASE_URL', 'http://localhost:5002')
    page_id = os.environ.get('FB_PAGE_ID') or os.environ.get('PAGE_ID') or '273719346452016'
    url = f"{base}/api/meta-report-content-insights?page_id={page_id}&limit=10"
    print('Testing:', url)
    r = requests.get(url, timeout=40)
    print('Status:', r.status_code)
    try:
        data = r.json()
    except Exception:
        print('Text:', r.text)
        return
    print('Keys:', list(data.keys()))
    print('Count posts:', data.get('count'))
    if data.get('ai', {}).get('insights'):
        print('AI insights sample:\n', data['ai']['insights'][:600])

if __name__ == '__main__':
    main()


