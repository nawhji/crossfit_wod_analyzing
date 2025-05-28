from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json
import pandas as pd
from collections import Counter
import re

# ✅ 정규화 함수
def normalize_movement_name(name: str, weight: float) -> str:
    name = name.lower()
    # name = re.sub(r'\bdb\b', 'dumbell', name)
    name = re.sub(r'\bdbs?\b', 'dumbell', name)  # db or dbs → dumbell
    name = re.sub(r'\bkb\b', 'kettlebell', name)

    dumbbell_keywords = ['dumbell', 'kettlebell']
    barbell_candidates = [
        'clean', 'clean and jerk', 'snatch', 'thruster', 'cluster',
        'squat', 'bench press', 'back rack lunge', 'front rack lunge', 'walking lunge',
        'push press', 'shoulder to overhead', 'push jerk', 'split jerk', 'jerk', 'anchor press',
        'ground to overhead', 'bodyweight deadlift', 'front squat', 'overhead squat', 'back rack', 'front rack',
        'shoulder to overhead', 'deadlift'
    ]
    dumbbell_candidates = [
        'devil press', 'burpee deadlift', 'deadlift burpee', 'goblet squat', 'turkish get up'
    ]

    if not any(k in name for k in dumbbell_keywords):
        for phrase in barbell_candidates:
            if phrase in name:
                if 'deadlift' in phrase and ('burpee' in name or weight <= 50):
                    continue
                if ('back rack' in phrase or 'front rack' in phrase) and weight <= 50:
                    continue
                if 'squat' in phrase and weight > 50:
                    name = 'barbell ' + name
                    continue
                name = 'barbell ' + name
                break

    for phrase in dumbbell_candidates:
        if phrase in name and not any(k in name for k in dumbbell_keywords):
            name = 'dumbell ' + name
            break
    
    if 'sdhp' in name and weight > 50:
        name = 'barbell sumo deadlift high pull'
    elif 'sdhp' in name and weight <= 50:
        name.replace('sdhp', 'sumo deadlift high pull')

    return name.strip()

# ✅ 모델 로딩
model = SentenceTransformer("../../bert_model/fine_tuned_crossfit_model/")

MAX_WEIGHT = 250
NULL_WEIGHT_VALUE = 0.5 * MAX_WEIGHT

# ✅ WOD 1개 → 벡터
def wod_to_vector(wod_json):
    try:
        if "type_reps" not in wod_json or not isinstance(wod_json["type_reps"], int) or wod_json["type_reps"] < 1:
            raise ValueError("Invalid or missing 'type_reps'")

        types = set()
        durations = []
        movements, counts, weights, increase_flags = [], [], [], []
        weight_bonus_factors = []

        num_type_reps = wod_json["type_reps"]
        for i in range(1, num_type_reps + 1):
            key = f"type_rep_{i}"
            rep = wod_json.get(key)
            if not rep:
                raise KeyError(f"Missing '{key}'")

            rep_type = rep.get("type")
            if rep_type is None:
                raise KeyError(f"Missing 'type' in {key}")
            types.add(rep_type)

            tc = rep.get("time_cap")
            durations.append(tc if isinstance(tc, (int, float)) else 0)

            for m in rep.get("movements", []):
                movement_name = m.get("movement")
                if not movement_name:
                    raise KeyError(f"Missing 'movement' in {key}")

                weight = m.get("weight", NULL_WEIGHT_VALUE)
                if weight is None:
                    weight = NULL_WEIGHT_VALUE

                normalized_name = normalize_movement_name(movement_name, weight)
                movements.append(normalized_name)

                count_raw = m.get("count", 0)
                if count_raw == -1:
                    count = 40
                elif isinstance(count_raw, str) and "-" in count_raw:
                    count = sum(map(int, count_raw.split("-")))
                elif isinstance(count_raw, int):
                    count = count_raw
                else:
                    count = 0

                # ✅ 거리 단위 보정
                if m.get("quantity", "") == "m":
                    count = count / 10
                elif m.get("quantity", "") == "ft":
                    count = count / 10

                # ✅ 더블언더 보정
                if "double under" in normalized_name:
                    count *= 0.2

                counts.append(count)
                weights.append(weight / MAX_WEIGHT)
                increase_flags.append(int(bool(m.get("increase", False))))

                # ✅ 무게 가중치 추가 계산
                raw_weight = weight
                if "barbell" in normalized_name and raw_weight >= 135:
                    weight_bonus_factors.append(raw_weight / 135)
                elif "dumbell" in normalized_name and raw_weight >= 50:
                    weight_bonus_factors.append(raw_weight / 50)
                elif "sandbag" in normalized_name and raw_weight >= 135:
                    weight_bonus_factors.append(raw_weight / 135)

        type_vector = [1 if t in types else 0 for t in ["AMRAP", "For Time", "EMOM"]]
        type_vector.append(1 if len(types) > 1 else 0)
        scaled_type_vector = 0.5 * np.array(type_vector)

        duration_norm = sum(durations) / (60 * wod_json["type_reps"])
        movement_embeddings = model.encode(movements)
        scaled_counts = [np.log1p(c) if c > 0 else 0 for c in counts]
        weights_sum = np.sum(scaled_counts)
        if weights_sum == 0:
            movement_embedding_avg = np.mean(movement_embeddings, axis=0)
        else:
            weights_np = np.array(scaled_counts) / weights_sum
            movement_embedding_avg = np.average(movement_embeddings, axis=0, weights=weights_np)

        count_mean = np.mean(scaled_counts)
        if wod_json.get("teamwod", False):
            count_mean *= 0.5

        movement_num = len(movements)
        increase_flag = int(any(increase_flags))
        weight_bonus = np.mean(weight_bonus_factors) if weight_bonus_factors else 0

        rest_type = [0, 0, 0]
        has_rest = False
        for i in range(1, wod_json["type_reps"] + 1):
            rep = wod_json.get(f"type_rep_{i}", {})
            if rep.get("onoff", False):
                rest_type[2] = 1
                has_rest = True
            elif any(m.get("is_rest", False) for m in rep.get("movements", [])):
                rest_type[1] = 1
                has_rest = True
        if not has_rest and wod_json.get("teamwod", False):
            rest_type[1] = 1
        elif not any(rest_type):
            rest_type[0] = 1

        scaled_non_embedding = np.array([
            *scaled_type_vector,
            duration_norm,
            num_type_reps,
            count_mean,
            movement_num,
            increase_flag,
            weight_bonus,
            *rest_type
        ]) * 40

        final_vector = np.concatenate([
            scaled_non_embedding,
            movement_embedding_avg
        ])
        return final_vector

    except Exception as e:
        return None, str(e)

# ✅ 모든 JSON 처리
def process_all_jsons_with_filenames(directory_path):
    vectors = []
    filenames = []
    errors = []

    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    wod_json = json.load(f)
                vec = wod_to_vector(wod_json)
                if isinstance(vec, tuple):
                    errors.append((filename, vec[1]))
                    print(f"❌ 실패: {filename} → {vec[1]}")
                else:
                    vectors.append(vec)
                    filenames.append(filename)
            except Exception as e:
                errors.append((filename, str(e)))
                print(f"❌ 실패: {filename} → {str(e)}")

    print(f"\n✅ 총 {len(vectors)}개 성공 / {len(errors)}개 실패")
    return vectors, filenames, errors

# ✅ 벡터 저장
def save_vectors(vectors, filenames, save_dir, prefix="wod_vectors"):
    os.makedirs(save_dir, exist_ok=True)
    np.save(os.path.join(save_dir, f"{prefix}.npy"), np.stack(vectors))
    pd.DataFrame(vectors).to_csv(os.path.join(save_dir, f"{prefix}.csv"), index=False)
    with open(os.path.join(save_dir, f"{prefix}_filenames.txt"), "w") as f:
        for name in filenames:
            f.write(name + "\n")
    print(f"✅ 저장 완료: {save_dir}/{prefix}.*")

# ✅ 메인 실행
def main(input_dir, output_dir, prefix="wod_vectors"):
    vectors, filenames, errors = process_all_jsons_with_filenames(input_dir)
    if vectors:
        save_vectors(vectors, filenames, output_dir, prefix)
    else:
        print("❌ 벡터 생성 실패")

    if errors:
        print("\n📄 오류 요약:")
        for fname, reason in errors:
            print(f" - {fname}: {reason}")

# ✅ 예시 실행
main("../../data/normed_data/panda/", ".", "panda")
