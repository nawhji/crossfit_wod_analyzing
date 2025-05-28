import glob
import os
import re

for file_path in glob.glob('unrefined/*.txt'):
    file_name = os.path.basename(file_path)
    d = file_name.replace('.txt', '')

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    start_key = '2024'
    end_key = 'Newer Posts'

    start = text.find(start_key)
    end = text.find(end_key)

    text = text[start + len(start_key):end]

    # wod_start = text.find('2024')
    # text = text[wod_start + len('2024'):]
    for i in range(9):
        wod_end = text.find('Coach’s notes:')
        temp = text.find('WOD Leaderboard')
        if wod_end == -1 or temp < wod_end:
            wod_end = temp
        wod = text[:wod_end]
        text = text[wod_end:]
        text = text[text.find('2024') + len('2024'):]

        wod = re.sub(r'\n\s*\n+', '\n', wod.strip())

        filename = f'refined/{d}_{i}.txt'
        with open(filename, 'w', encoding='utf-8') as f_out:
            f_out.write(wod)
    
    wod_end = text.find('Coach’s notes:')
    temp = text.find('WOD Leaderboard')
    if wod_end == -1 or temp < wod_end:
        wod_end = temp
    text = text[:wod_end]
    text = re.sub(r'\n\s*\n+', '\n', text.strip())
    with open(f'refined/{d}_9.txt', 'w', encoding='utf-8') as f_out:
        f_out.write(text)