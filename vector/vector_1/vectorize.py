# Re-import after reset
import os
import numpy as np
import json
import pandas as pd
from collections import Counter
import re
from sentence_transformers import SentenceTransformer

# ✅ 정규화 함수
def normalize_movement_name(name: str, weight: float) -> str:
    name = name.lower()
    name = re.sub(r'\bdb\b', 'dumbell', name)
    name = re.sub(r'\bkb\b', 'kettlebell', name)

    dumbbell_keywords = ['dumbell', 'kettlebell']
    barbell_candidates = [
        'clean', 'clean and jerk', 'snatch', 'thruster', 'cluster',
        'back squat', 'bench press', 'back rack lunge', 'front rack lunge', 'walking lunge',
        'push press', 'shoulder to overhead', 'push jerk', 'split jerk', 'jerk', 'anchor press',
        'ground to overhead', 'bodyweight deadlift', 'front squat', 'overhead squat'
    ]
    dumbbell_candidates = [
        'devil press', 'burpee deadlift', 'deadlift burpee', 'goblet squat', 'turkish get up'
    ]

    if not any(k in name for k in dumbbell_keywords):
        for phrase in barbell_candidates:
            if phrase in name:
                if 'deadlift' in phrase and ('burpee' in name or weight <= 50):
                    continue
                name = 'barbell ' + name
                break

    for phrase in dumbbell_candidates:
        if phrase in name and not any(k in name for k in dumbbell_keywords):
            name = 'dumbell ' + name
            break

    return name.strip()

# ✅ 모델 로딩
model = SentenceTransformer("../bert_model/fine_tuned_crossfit_model/")

MAX_WEIGHT = 250
NULL_WEIGHT_VALUE = 0.65 * MAX_WEIGHT

# ✅ WOD 1개 → 벡터
def wod_to_vector(wod_json):
    try:
        if "type_reps" not in wod_json or not isinstance(wod_json["type_reps"], int) or wod_json["type_reps"] < 1:
            raise ValueError("Invalid or missing 'type_reps'")

        types = set()
        durations = []
        movements, counts, weights, increase_flags = [], [], [], []
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
                counts.append(count)

                weights.append(weight / MAX_WEIGHT)
                increase_flags.append(int(bool(m.get("increase", False))))

        type_vector = [1 if t in types else 0 for t in ["AMRAP", "For Time", "EMOM"]]
        type_vector.append(1 if len(types) > 1 else 0)

        duration_norm = sum(durations) / (60 * num_type_reps)
        movement_embeddings = model.encode(movements)
        movement_embedding_avg = np.mean(movement_embeddings, axis=0)

        scaled_counts = [np.log1p(c) if c > 0 else 0 for c in counts]
        count_mean = np.mean(scaled_counts)
        if wod_json.get("teamwod", False):
            count_mean *= 0.5

        weight_mean = np.mean(weights)
        weight_max = max(weights)
        movement_num = len(movements)
        increase_flag = int(any(increase_flags))

        has_rest = wod_json.get("rest_between", False)
        for i in range(1, wod_json["type_reps"] + 1):
            rep = wod_json.get(f"type_rep_{i}", {})
            if rep.get("rest", False):
                has_rest = True
                break
        rest_flag = int(has_rest)

        final_vector = np.concatenate([
            type_vector,
            [duration_norm],
            [num_type_reps],
            movement_embedding_avg,
            [count_mean, weight_mean, weight_max],
            [movement_num, increase_flag],
            [rest_flag]
        ])
        return final_vector

    except Exception as e:
        return None, str(e)

# ✅ 모든 폴더 순회 및 JSON 처리
def process_all_jsons_recursively(root_dir):
    vectors = []
    filenames = []
    errors = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        wod_json = json.load(f)
                    vec = wod_to_vector(wod_json)
                    if isinstance(vec, tuple):
                        errors.append((file_path, vec[1]))
                        print(f"❌ 실패: {file_path} → {vec[1]}")
                    else:
                        vectors.append(vec)
                        filenames.append(file_path)
                except Exception as e:
                    errors.append((file_path, str(e)))
                    print(f"❌ 실패: {file_path} → {str(e)}")

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

# ✅ 실행
input_dir = "../data/normed_data/"
output_dir = "vector_1/"
prefix = "all"

vectors, filenames, errors = process_all_jsons_recursively(input_dir)
if vectors:
    save_vectors(vectors, filenames, output_dir, prefix)
else:
    print("❌ 벡터 생성 실패")

if errors:
    print("\n📄 오류 요약:")
    for fname, reason in errors:
        print(f" - {fname}: {reason}")
