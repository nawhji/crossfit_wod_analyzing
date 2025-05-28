import requests
from bs4 import BeautifulSoup

url = 'https://crossfitcalgary.ca/wod/'
html = requests.get(url).text

soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text(separator='\n')

with open('forte.txt', 'w', encoding='utf-8') as f:
    f.write(text)