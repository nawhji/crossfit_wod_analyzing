from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import os

# 저장 폴더
os.makedirs('unrefined', exist_ok=True)

# 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 날짜 생성: 2023-08-01 ~ 2023-11-30
start_date = datetime(2023, 12, 1)
end_date = datetime(2024, 1, 31)
delta = timedelta(days=1)

current = start_date
while current <= end_date:
    month_name = current.strftime('%B').lower()   # august, september, ...
    day = current.day
    year = current.year

    # URL 생성
    url = f'https://tamcrossfit.com/tamalpais-crossfit-wod-{month_name}-{day}-{year}/'
    print(f'Crawling {url}...')

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
    except:
        print(f'⚠️ Warning: {current.strftime("%Y-%m-%d")} not properly loaded.')

    # 페이지 HTML 파싱
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')
    text = soup.get_text(separator='\n', strip=False)

    # 저장
    save_name = current.strftime('%Y%m%d')  # 예: 20230801
    with open(f'unrefined/{save_name}.txt', 'w', encoding='utf-8') as f:
        f.write(text)

    time.sleep(5)
    current += delta

# 드라이버 종료
driver.quit()
