import glob
import re

for file_path in glob.glob('refined/*.txt'):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # ♀ 이후 내용 제거
    cut_index = text.find('♀')
    if cut_index != -1:
        text = text[:cut_index]

    # 연속된 newline을 하나로 축소
    text = re.sub(r'\n\s*\n+', '\n', text).strip()

    # 결과 덮어쓰기
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
