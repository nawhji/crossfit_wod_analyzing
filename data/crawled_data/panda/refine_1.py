import glob
import os
import re

for file_path in glob.glob('refined/*.txt'):
    file_name = os.path.basename(file_path)
    d = file_name.replace('.txt', '')
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    text = re.sub(r'\n\s*\n+', '\n', text.strip())

    # 저장
    filename = f'refined_1/{d}.txt'
    with open(filename, 'w', encoding='utf-8') as f_out:
        f_out.write(text)