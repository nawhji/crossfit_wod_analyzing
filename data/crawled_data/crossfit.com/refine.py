import glob
import os
import re

for file_path in glob.glob('unrefined/*.txt'):
    file_name = os.path.basename(file_path)
    d = file_name.replace('.txt', '')  # 파일명에서 날짜 추출

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    if 'Rest Day' in text:
        continue

    start_key = f'{d}\nWorkout of the Day'
    start = text.find(start_key)
    end_scaling = text.find('Scaling')
    end_strategy = text.find('Stimulus and Strategy:')

    # 적절한 종료 위치 선택
    if end_scaling != -1:
        end = end_scaling
    elif end_strategy != -1:
        end = end_strategy
    else:
        print(f'error - day {d} (no end key)')
        continue

    if start == -1 or end == -1:
        print(f'error - day {d} (start or end not found)')
        continue

    # 중간 블록 추출
    temp = text[start + len(start_key):end].strip()
    comments = temp.find('\n')
    content = temp[comments + 1:] if comments != -1 else temp

    # 'Post' 이후 제거
    post_idx = content.find('Post')
    if post_idx != -1:
        content = content[:post_idx]

    # 'Compare to' 이후 제거
    compare_idx = content.find('Compare to')
    if compare_idx != -1:
        content = content[:compare_idx]

    # 공백 제거 + 중복 newline 제거
    content = re.sub(r'\n\s*\n+', '\n', content.strip())

    # 저장
    filename = f'refined/{d}.txt'
    with open(filename, 'w', encoding='utf-8') as f_out:
        f_out.write(content)