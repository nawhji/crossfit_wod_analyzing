import re
from typing import Optional

def normalize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[-_]", " ", name)
    name = re.sub(r"\s+", " ", name).strip() 
    name = re.sub(r"s\b", "", name)                 
    
    if "pres " in name or name.endswith("pres"):
        name = name.replace("pres", "press")
    if "toe " in name:
        name = name.replace("toe", "toes")

    return name

movement_type_keywords = {
    "plyometric": [
        "jump", "hop", "jumping", "tuck up", "tuckup", "hop", 
        "burpee over", "burpee to", "lateral burpee", "facing burpee"
    ],
    "cardio": [
        "row", "ski", "bike", "echo", "erg", "shuttle", "run", "sprint",
        "jump rope", "double under", "crossover", "reverse double under",
        "burpee", 'ruck'
    ],
    "bodyweight": [
        "air squat", "push up", "hand-release push up", "ring push up",
        "pike push up", "lunge", "walking lunge", "shoulder tap", "dip",
    ],
    "gymnastics": [
        "rope climb", "muscle up", "muscle-up", "ring", "pull over", "toes to",
        "knee raise", "knees to elbows", 'knee to elbow', "peg board", "pull up", "pull-up", "pullup",
        "bar dip", "handstand", "wall walk", "chest to bar",
    ],
    "full_body": [
        "medicine ball clean", "wall ball shot", "step up", "wallball", "wall ball",
        "devil press"
    ],
    "core": [
        "sit up", "sit-up", "situp", "ghd", "plank", "v up", "flutter", "superman",
        "l sit", "hollow", "russian twist", "back extension",
        "seated leg raise", "dead hang", "mountain climber", 'turkish get up',
        'hip extension', 'candlestick rock'
    ]
}

dumbbell_keywords = ['dumbbell', 'db', 'kettlebell', 'kb']
odd_keywords = ['sandbag', 'odd', 'sled']

barbell_keywords = [
    'clean', 'clean and jerk', 'snatch', 'thruster', 'cluster',
    'squat', 'press', 'back rack', 'front rack', 'walking lunge',
    'push press', 'shoulder to overhead', 'push jerk', 'split jerk', 'jerk', 'anchor press',
    'ground to overhead', 'bodyweight deadlift', 'deadlift', 'sdhp'
]

lunge_keywords = ['lunge', 'walking lunge', 'back rack lunge', 'front rack lunge']

dumbbell_candidates = [
    'burpee deadlift', 'deadlift burpee', 'goblet squat'
]

def get_movement_type(name: str, weight: Optional[float]) -> str:
    name = normalize_name(name)

    if "carry" in name or 'hold' in name:
        return "carry"

    if any(k in name for k in dumbbell_keywords):
        return "dumbbell"
    if any(k in name for k in dumbbell_candidates):
        return "dumbbell"
    if any(k in name for k in odd_keywords):
        return "full_body"

    if any(k in name for k in barbell_keywords):
        if not any(k in name for k in dumbbell_keywords):
            if "deadlift" in name and "burpee" in name:
                return "unknown"
            return "barbell"
    if any(k in name for k in lunge_keywords):
        if not any(k in name for k in dumbbell_keywords) and weight and weight > 0:
            return "barbell"

    for category, keywords in movement_type_keywords.items():
        for kw in keywords:
            if kw in name:
                return category

    return "unknown"

############

import os
import json
from collections import Counter

unknown_movements = set()
overall_movement_counter = Counter()
overall_type_counter = Counter()
overall_barbell_weights = []

output_dir = "cluster_analysis_result"
os.makedirs(output_dir, exist_ok=True)

def get_all_movements(data: dict) -> list:
    movements = []
    for key in data:
        if key.startswith("type_rep_"):
            block = data[key]
            if isinstance(block, dict):
                for m in block.get("movements", []):
                    movements.append(m)
    return movements

base_dir = "cluster_files_kmeans/json"
cluster_dirs = sorted([d for d in os.listdir(base_dir) if d.startswith("cluster_")])

for cluster_dir in cluster_dirs:
    full_path = os.path.join(base_dir, cluster_dir)
    json_files = [f for f in os.listdir(full_path) if f.endswith(".json")]

    movement_counter = Counter()
    type_counter = Counter()
    barbell_weights = []

    for json_file in json_files:
        with open(os.path.join(full_path, json_file), 'r', encoding='utf-8') as f:
            data = json.load(f)

        movements = get_all_movements(data)
        for move in movements:
            raw_name = move.get("movement", "")
            name = normalize_name(raw_name)
            weight = move.get("weight", None)

            movement_counter[name] += 1
            overall_movement_counter[name] += 1

            movement_type = get_movement_type(name, weight)
            type_counter[movement_type] += 1
            overall_type_counter[movement_type] += 1

            if movement_type == "barbell" and weight is not None:
                barbell_weights.append(weight)
                overall_barbell_weights.append(weight)

            if movement_type == "unknown":
                unknown_movements.add(name)

    most_common_type, most_common_count = type_counter.most_common(1)[0] if type_counter else ("none", 0)
    avg_barbell_weight = round(sum(barbell_weights) / len(barbell_weights), 2) if barbell_weights else "N/A"
    top_15 = movement_counter.most_common(15)

    output_path = os.path.join(output_dir, f"{cluster_dir}_summary.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"📁 {cluster_dir} analysis result\n")
        f.write(f"# of WOD: {len(json_files)}개\n")
        f.write(f"\n✅ dominant WOD type: {most_common_type} ({most_common_count} times)\n")
        f.write(f"🏋️ barbell weight average: {avg_barbell_weight}\n")
        f.write("\n🔝 Top 15 Movement:\n")
        for name, count in top_15:
            f.write(f"  {name:30} {count}\n")
        f.write("\n📊 WOD type ratio\n")
        total = sum(type_counter.values())
        for k, v in type_counter.items():
            ratio = v / total if total > 0 else 0
            f.write(f"  {k:10}: {v} ({ratio:.1%})\n")

unknown_path = os.path.join(output_dir, "unknown_movements.txt")
with open(unknown_path, "w", encoding="utf-8") as f:
    f.write("❓ Unknown movements\n\n")
    for name in sorted(unknown_movements):
        f.write(f"{name}\n")

overall_output_path = os.path.join(output_dir, "overall_summary.txt")
with open(overall_output_path, "w", encoding="utf-8") as f:
    f.write("📊 Overall WOD stats\n")
    f.write(f"총 movement 발생 수: {sum(overall_movement_counter.values())}\n")
    f.write(f"총 운동 유형 분류 수: {sum(overall_type_counter.values())}\n")

    f.write("\n🔝 Top 30 Movement 전체 기준:\n")
    for name, count in overall_movement_counter.most_common(30):
        f.write(f"  {name:30} {count}\n")

    f.write("\n📊 전체 운동 유형 비율:\n")
    total = sum(overall_type_counter.values())
    for k, v in overall_type_counter.items():
        ratio = v / total if total > 0 else 0
        f.write(f"  {k:10}: {v} ({ratio:.1%})\n")

    avg_overall_barbell_weight = round(sum(overall_barbell_weights) / len(overall_barbell_weights), 2) if overall_barbell_weights else "N/A"
    f.write(f"\n🏋️ 전체 평균 바벨 무게: {avg_overall_barbell_weight}\n")