import glob
import os
import difflib

def approx_find(text, keyword, threshold=0.85):
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    best_score = 0
    best_index = -1

    for i in range(len(text) - len(keyword) + 1):
        window = text_lower[i:i+len(keyword)]
        score = difflib.SequenceMatcher(None, window, keyword_lower).ratio()
        if score > threshold and score > best_score:
            best_score = score
            best_index = i

    return best_index

# 오류 저장 디렉토리 생성
os.makedirs('error', exist_ok=True)
os.makedirs('refined', exist_ok=True)

for file_path in glob.glob('unrefined/*.txt'):
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        contents = f.read()

        start_key = "CrossFit W.O.D:"
        mid_key = "CrossFit Strength:"
        end_key = "Read more"

        start = approx_find(contents, start_key)
        mid = approx_find(contents, mid_key)
        end = approx_find(contents, end_key)
        if mid >= end:
            mid = -1

        if start == -1 or end == -1:
            print(f'error - day {file_path} (start or end not found)')
            base_name = os.path.basename(file_path)
            with open(f'error/{base_name}', 'w', encoding='utf-8') as ef:
                ef.write(contents)
            continue

        if mid == -1:
            wod = contents[start:end]
        else:
            wod = contents[start:mid]
            strength = contents[mid:end]
            strength_metcon = approx_find(strength, "Metcon:")
            if strength_metcon != -1:
                keylen_metcon = len("Metcon:")
                result.append(strength[strength_metcon + keylen_metcon:].strip())

        wod_metcon = approx_find(wod, "Metcon:")
        keylen_metcon = len("Metcon:")

        if wod_metcon == -1:
            print(f"error - no metcon found in {file_path}")
            base_name = os.path.basename(file_path)
            with open(f'error/{base_name}', 'w', encoding='utf-8') as ef:
                ef.write(contents)
            continue

        next_keywords = [
            approx_find(wod, "Endurance:"),
            approx_find(wod, "CrossFit Endurance:"),
            approx_find(wod, "Strength:"),
            approx_find(wod, "Gymnastics:"),
            approx_find(wod, "Weightlifting:")
        ]

        end_index = end
        for idx in next_keywords:
            if idx != -1 and idx > wod_metcon:
                end_index = min(end_index, idx)

        result.append(wod[wod_metcon + keylen_metcon:end_index].strip())

    base_name = os.path.basename(file_path).replace(".txt", "")
    for i, text in enumerate(result):
        output_path = f'refined/{base_name}_{i}.txt'
        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.write(text)
