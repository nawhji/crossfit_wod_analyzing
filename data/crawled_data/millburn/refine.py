# start key : Workout:
# end key : Today's WOD

import glob
import os
import re

os.makedirs('error', exist_ok=True)
os.makedirs('refined', exist_ok=True)

for file_path in glob.glob('unrefined/*.txt'):
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        contents = f.read()

        start_key = "Workout:"
        end_key = "Today's WOD"

        start = contents.find(start_key)
        end = contents.find(end_key)

        if start == -1 or end == -1:
            print(f'error - day {file_path} (start or end not found)')
            base_name = os.path.basename(file_path)
            with open(f'error/{base_name}', 'w', encoding='utf-8') as ef:
                ef.write(contents)
            continue

        contents = contents[start:end]

        workout = contents.find("Workout:")
        cardio = contents.find("Cardio Option:")

        workout_end = contents.find("————————————————")
        wod = contents[workout + len("Workout:"):workout_end]
        wod = re.sub(r'\n\s*\n+', '\n', wod)
        result.append(wod.strip())

        if cardio != -1:
            contents = contents[cardio + (len("Cardio Option: ")):].strip()
            cardio_end = contents.find("————————————————")
            cardio_wod = contents[:cardio_end]
            cardio_wod = re.sub(r'\n\s*\n+', '\n', cardio_wod)
            result.append(cardio_wod.strip())

    base_name = os.path.basename(file_path).replace(".txt", "")
    for i, text in enumerate(result):
        output_path = f'refined/{base_name}_{i}.txt'
        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.write(text)
