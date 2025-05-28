import glob
import os
import re

for file_path in glob.glob('unrefined/*.txt'):
    file_name = os.path.basename(file_path)
    d = file_name.replace('.txt', '')

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    start_key = 'OUR WODS'
    end_key = '« Previous'

    start = text.find(start_key)
    end = text.find(end_key)

    text = text[start + len(start_key):end]

    wod_start = text.find('2024')
    text = text[wod_start + len('2024'):]
    for i in range(6):
        wod_end = text.find('2024')
        wod = text[:wod_end - 6]
        text = text[wod_end + len('2024'):]

        filename = f'refined/{d}_{i}.txt'
        with open(filename, 'w', encoding='utf-8') as f_out:
            f_out.write(wod.strip())
    
    with open(f'refined/{d}_6.txt', 'w', encoding='utf-8') as f_out:
        f_out.write(text.strip())