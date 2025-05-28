import glob
import os

for file_path in glob.glob('unrefined/020525.txt'):
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        contents = f.read()

        start_key = "CrossFit W.O.D:"
        mid_key = "CrossFit Strength:"
        end_key = "Read more"

        start = contents.find(start_key)
        mid = contents.find(mid_key)
        end = contents.find(end_key)
        if mid >= end: mid = -1

        if start == -1 or end == -1:
            print(f'error - day {file_path}')
            continue

        with open("end.txt", 'w', encoding='utf-8') as f_out:
            f_out.write(contents[start:end].strip())

        if mid == -1:
            wod = contents[start:end]
            wod_metcon = wod.find("Metcon:")
            wod_endurance = wod.find("Endurance:")

            wod_gymnastic = wod.find("Gymnastics:")
            wod_strength = wod.find("Strength:")
            wod_weightlifting = wod.find("Weightlifting:")

            if wod_gymnastic == -1 and wod_strength == -1 and wod_weightlifting == -1:
                end_index = end
            elif all(x == -1 for x in [wod_gymnastic, wod_strength]) and (wod_weightlifting > wod_endurance or wod_weightlifting > wod_metcon):
                end_index = wod_weightlifting
            elif all(x == -1 for x in [wod_gymnastic, wod_weightlifting]) and (wod_strength > wod_endurance or wod_strength > wod_metcon):
                end_index = wod_strength
            elif all(x == -1 for x in [wod_strength, wod_weightlifting]) and (wod_gymnastic > wod_endurance or wod_gymnastic > wod_metcon):
                end_index = wod_gymnastic
            else:
                candidates = [idx for idx in [wod_gymnastic, wod_strength, wod_weightlifting]
                            if idx > wod_endurance or idx > wod_metcon and idx != -1]
                end_index = min(candidates) if candidates else end

            keylen_metcon = len("Metcon:")
            keylen_endurance = len("Endurance:")

            if (wod.find("CrossFit Endurance:") != -1):
                wod_endurance = wod.find("CrossFit Endurance")
                keylen_endurance = len("CrossFit Endurance")

            if wod_endurance == -1:
                result.append((wod[wod_metcon + keylen_metcon:end_index]).strip())
            else:
                result.append((wod[wod_metcon + keylen_metcon:wod_endurance]).strip())
                result.append((wod[wod_endurance + keylen_endurance:end_index]).strip())
        
        else:
            wod = contents[start:mid]
            strength = contents[mid:end]

            wod_metcon = wod.find("Metcon:")
            wod_endurance = wod.find("Endurance:")
            strength_metcon = strength.find("Metcon:")

            wod_gymnastic = wod.find("Gymnastics:")
            wod_strength = wod.find("Strength:")
            wod_weightlifting = wod.find("Weightlifting:")

            if wod_gymnastic == -1 and wod_strength == -1 and wod_weightlifting == -1:
                end_index = end
            elif all(x == -1 for x in [wod_gymnastic, wod_strength]) and (wod_weightlifting > wod_endurance or wod_weightlifting > wod_metcon):
                end_index = wod_weightlifting
            elif all(x == -1 for x in [wod_gymnastic, wod_weightlifting]) and (wod_strength > wod_endurance or wod_strength > wod_metcon):
                end_index = wod_strength
            elif all(x == -1 for x in [wod_strength, wod_weightlifting]) and (wod_gymnastic > wod_endurance or wod_gymnastic > wod_metcon):
                end_index = wod_gymnastic
            else:
                candidates = [idx for idx in [wod_gymnastic, wod_strength, wod_weightlifting]
                            if idx > wod_endurance or idx > wod_metcon and idx != -1]
                end_index = min(candidates) if candidates else end

            keylen_metcon = len("Metcon:")
            keylen_endurance = len("Endurance:")

            if (wod.find("CrossFit Endurance:") != -1):
                wod_endurance = wod.find("CrossFit Endurance")
                keylen_endurance = len("CrossFit Endurance")

            if not strength_metcon == -1:
                result.append((strength[strength_metcon + keylen_metcon:]).strip())

            if wod_endurance == -1:
                result.append((wod[wod_metcon + keylen_metcon:end_index]).strip())
            else:
                result.append((wod[wod_metcon + keylen_metcon:wod_endurance]).strip())
                result.append((wod[wod_endurance + keylen_endurance:end_index]).strip())

    base_name = os.path.basename(file_path).replace(".txt", "")
    # print(f"result length: {len(result)}")
    for i, text in enumerate(result):
        output_path = f'new_{base_name}_{i}.txt'
        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.write(text)