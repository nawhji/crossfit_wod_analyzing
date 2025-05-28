import os
import glob

folder_path = 'output/panda'
json_files = glob.glob(os.path.join(folder_path, '*.json'))

for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 문자열 치환
    new_content = content.replace('"emom_time_per_round"', '"emom_num_movements"')

    # 다시 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("✅ 모든 JSON 파일에서 문자열 치환 완료!")
