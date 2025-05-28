from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime, timedelta

os.makedirs('unrefined', exist_ok=True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

day_in_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
month_name = ["january", "february", "march", "april", "may"]

# 날짜 리스트 생성 (2025-01-31 ~ 2025-05-13)
date = []
start_date = datetime(2025, 1, 31)
end_date = datetime(2025, 5, 13)
current = start_date
while current <= end_date:
    date.append([current.month, current.day, current])
    current += timedelta(days=1)

day_num = 5
burpee_day_num = 5

for i in range(len(date) - 1):  # date[i+1]을 쓰기 위해 마지막 날은 제외
    t = 'th'
    if not 11 <= date[i+1][1] <= 13:
        if date[i+1][1] == 1 or date[i+1][1] == 21:
            t = 'st'
        elif date[i+1][1] == 2 or date[i+1][1] == 22:
            t = 'nd'
        elif date[i+1][1] == 3 or date[i+1][1] == 23:
            t = 'rd'

    url = f'https://crossfitmillburn.com/2025/{date[i][0]:02d}/{date[i][1]:02d}/wod-' \
          f'{day_in_week[day_num]}-{month_name[date[i+1][0]-1]}-{date[i+1][1]}{t}-2025-burpee-day-{burpee_day_num}'
    print(f'Crawling {url}...')

    burpee_day_num += 1
    day_num = (day_num + 1) % 7

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Workout of the Day')
        )
    except:
        print(f'Warning: day {date[i+1][0]}/{date[i+1][1]} not properly loaded.')

    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')
    text = soup.get_text(separator='\n', strip=False)

    with open(f'unrefined/{date[i+1][0]}-{date[i+1][1]}.txt', 'w', encoding='utf-8') as f:
        f.write(text)

    time.sleep(10)

driver.quit()