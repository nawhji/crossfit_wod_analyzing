from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os

# 0. 저장 폴더가 없으면 생성
os.makedirs('unrefined', exist_ok=True)

# 1. 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 2. 날짜 리스트 만들기
date = []
for month in range(1, 5):
    if (month < 7 and month % 2 == 1) or (month > 7 and month % 2 == 0) or month == 7:
        max_day = 31
    elif (month < 7 and month != 2) or (month > 7):
        max_day = 30
    elif month == 2:
        max_day = 28

    if month == 4:
        max_day = 28

    start_day = 1
    if month == 5:
        max_day = 15

    for day in range(start_day, max_day + 1):
        date.append(f'24{month:02d}{day:02d}')

# 3. 크롤링 루프
for d in date:
    url = f'https://www.crossfit.com/{d}'
    print(f'Crawling {url}...')

    driver.get(url)

    # 페이지 안에 날짜가 뜰 때까지 대기 (최대 10초)
    try:
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), d)
        )
    except:
        print(f'Warning: {d} not properly loaded.')

    # 페이지 HTML 파싱
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')
    text = soup.get_text(separator='\n', strip=False)

    # 저장
    with open(f'unrefined/{d}.txt', 'w', encoding='utf-8') as f:
        f.write(text)

    # 사이트 블락 방지용 딜레이
    time.sleep(5)

# 4. 드라이버 종료
driver.quit()
