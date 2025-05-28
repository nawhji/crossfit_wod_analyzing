import glob
import os
import re

for file_path in glob.glob('unrefined/*.txt'):
    file_name = os.path.basename(file_path)
    d = file_name.replace('.txt', '')

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    temp = text  # 원본 복사
    temp_lower = temp.lower()  # 비교용 소문자 복사본

    if 'grizzly' not in temp_lower:
        continue

    if 'grizzly & kodiak' in temp_lower:
        start_idx = temp_lower.find('grizzly & kodiak')
        content = temp[start_idx + len('grizzly & kodiak- '):].strip()

    elif 'kodiak' in temp_lower:
        start_idx = temp_lower.find('grizzly')
        end_idx = temp_lower.find('kodiak')
        content = temp[start_idx + len('grizzly- '):end_idx].strip()

    else:
        continue

    content = re.sub(r'\n\s*\n+', '\n', content.strip())

    with open(f'refined/{d}.txt', 'w', encoding='utf-8') as f_out:
        f_out.write(content)
