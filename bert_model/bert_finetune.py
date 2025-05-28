from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import random
import os

group_to_movements = {
    "Core": [
        "Flutter kick", "Good Morning", "Hollow rock", "L-sit hold", "Plank Hold",
        "Russian twist", "Sit-up", "Superman", "V-up", "Wall ball sit up", "wall ball hanging knee raise",
        "GHD", 
    ],
    "Shoulder (+Core)": [
        "dumbell Push press", "Handstand Hold", "Handstand push up", "Handstand walk",
        "Shoulder tap", "Strict handstand push up", "Wall facing strict handstand push up",
        "Wall-facing handstand shoulder tap"
    ],
    "Back (+Core)": [
        "Chest to bar pull up", "Dumbell renegade rows", "Jumping pull up",
        "Peg board ascents", "Pull over", "Pull up", "Ring row", "Strict Chest to bar pull up",
        "Strict Pull up", "Strict Ring Muscle up", "Strict Toes to bar", "barbell Sumo deadlift high pull",
        "Toes to bar", "Toes to ring", "Weighted Pull up", "burpee over the rower"
    ],
    "Lower Body": [
        "Air squat", "Back Squat", "dumbell hang squat clean", "dumbell hang squat snatch",
        "dumbell squat clean", "dumbell squat snatch", "Dumbell overhead walking lunge",
        "barbell Frankenstein Front Squat", "Front Squat", "Goblet Squat", "barbell Hang Squat Clean",
        "barbell Hang Squat Snatch", "Lunge", "Medicine ball squat", "Overhead Plate lunge",
        "barbell Overhead squat", "Pistol squat", "barbell Squat Clean", "barbell Squat Snatch", "Walking Lunge", "Deadlift",
        "box jump", "box step up", "medicine ball", "wall ball"
    ],
    "Lifting": [
        "Bench press", "barbell Bodyweight Deadlift", "barbell Clean and Jerk", "barbell Cluster",
        "barbell Deadlift",
        "barbell Hang Power Clean", "barbell Hang Power Snatch",
        "barbell Hang Squat Clean", "barbell Hang Squat Snatch",
        "barbell Overhead squat", "barbell Power Clean", "barbell Power Snatch", "Snatch",
        "barbell Squat Clean", "barbell Squat Snatch", "barbell Sumo deadlift", "barbell Sumo deadlift high pull",
        "barbell Thruster", "Sandbag Clean", "Sandbag Clean and Jerk"
    ],
    "weightlift + Forearm (Hang)": [
        "barbell Hang Power Clean", "barbell Hang Power Snatch", "barbell Hang Squat Clean", "barbell Hang Squat Snatch"
    ],
    "Tabata": [
        "Box Jump", "Box Jump over", "Box step up", "Burpee",
        "Burpee Box Jump", "Burpee Box Jump over", "Burpee Pull up", "dumbell step up",
        "Double under", "Jumping pull up", "Reverse Double under", "Skipping", "bar facing burpee",
        "burpee over the bar", "burpee over the dumbell", "burpee over the rower",
        "burpee to plate", "burpee to target", "row", "run", "erg", "ski", "weighted run", "ruck",
        "echo bike", "bike", "lateral bar hops", "bar hops"
    ],
    "Total Body": [
        "dumbell Push press", "Thruster", "dumbell Windmill", "dumbell hang clean",
        "dumbell hang snatch", "dumbell hang squat clean", "dumbell hang squat snatch",
        "dumbell squat clean", "dumbell squat snatch",
        "Dumbell Clean and Jerk", "Dumbell Snatch", "Dumbell front rack hold",
        "Dumbell hold", "Dumbell overhead walking lunge", "Dumbell renegade rows",
        "kettlebell Push press", "Thruster", "kettlebell Windmill", "kettlebell hang clean",
        "kettlebell hang snatch", "kettlebell hang squat clean", "kettlebell hang squat snatch",
        "kettlebell squat clean", "kettlebell squat snatch",
        "kettlebell Clean and Jerk", "kettlebell Snatch", "kettlebell front rack hold",
        "kettlebell hold", "kettlebell overhead walking lunge", "kettlebell renegade rows",
        "kettlebell Swing", "Russian kettlebell Swing", "Dumbell Turkish get up",
        "Box (sled) push", "cluster", "wall ball shot", "medicine ball", "Sandbag over shoulder",
        "Sandbag bearhug walk"
    ],
    "Gymnastics": [
        "Bar Muscle up", "Bar dip", "Burpee Pull up", "Chest to bar pull up",
        "Handstand Hold", "Handstand push up", "Handstand walk", "Jumping pull up", "Peg board ascents",
        "Pull up", "Ring Muscle up", "Ring dip", "Ring support hold", "Rope climb",
        "Strict Chest to bar pull up", "Strict Pull up", "Strict Ring Muscle up", "Strict Toes to bar",
        "Strict handstand push up", "Toes to bar", "Toes to ring", "Wall facing strict handstand push up",
        "Wall walk", "Wall-facing handstand shoulder tap", "Weighted Pull up", "legless rope climb",
        "Bear Crawl", "Knee raise", "Knees to elbows", "Dead hang", "pull over"
    ],
    "Arms + Chest": [
        "Bar dip", "Hand-release push up", "Handstand push up", "Pike push up", "Push up",
        "Ring dip", "Ring push up", "Shoulder tap", "Strict handstand push up",
        "Wall facing strict handstand push up", "Wall-facing handstand shoulder tap",
        "Ring row", "Ring support hold"
    ]
}

def generate_triplets(group_to_movements, num_triplets_per_group=30):
    triplets = []
    groups = list(group_to_movements.keys())

    for group in groups:
        positives = group_to_movements[group]
        if len(positives) < 2:
            continue
        for _ in range(num_triplets_per_group):
            a, p = random.sample(positives, 2)
            other_groups = [g for g in groups if g != group and len(group_to_movements[g]) > 0]
            n = random.choice(group_to_movements[random.choice(other_groups)])
            triplets.append(InputExample(texts=[a, p, n]))
    return triplets

def get_hard_triplets():
    return [
        # 덤벨 vs 바벨 구분 (같은 기능, 다른 장비)
        InputExample(texts=["dumbell Push press", "dumbell Thruster", "barbell Push press"]),
        InputExample(texts=["dumbell hang clean", "dumbell squat clean", "barbell Hang Power Clean"]),
        InputExample(texts=["dumbell hang snatch", "dumbell hang squat snatch", "barbell Power Snatch"]),
        InputExample(texts=["Dumbell Clean and Jerk", "Dumbell Snatch", "barbell Clean and Jerk"]),
        InputExample(texts=["dumbell hang squat clean", "dumbell hang clean", "barbell Squat Clean"]),

        # 푸시업류 vs 매달리는 동작 구분
        InputExample(texts=["Push up", "Hand-release push up", "Pull up"]),
        InputExample(texts=["Ring push up", "Pike push up", "Chest to bar pull up"]),
        # InputExample(texts=["Handstand push up", "Strict handstand push up", "Rope climb"]),
        # InputExample(texts=["Ring dip", "Bar dip", "Ring Muscle up"]),
        # InputExample(texts=["Push up", "Shoulder tap", "Ring row"]),

        # 더 헷갈릴 수 있는 트리오
        # InputExample(texts=["Wall-facing handstand shoulder tap", "Handstand Hold", "Pull over"]),
        # InputExample(texts=["L-sit hold", "Plank Hold", "Dead Hang"]),
        InputExample(texts=["Flutter kick", "Hollow rock", "Knees to elbows"]),
        # InputExample(texts=["Sit-up", "Superman", "Toes to bar"]),
        InputExample(texts=["Dumbell Thruster", "Dumbell devil press", "Burpee over the dumbell"]),
        InputExample(texts=["Dumbell Step up", "Box jump", "Dumbell devil press"]),
        # InputExample(texts=["Wall ball sit up", "Wall ball shot", "barbell Thruster"]),
        InputExample(texts=["kettlebell Swing", "kettlebell renegade rows", "barbell Squat Clean"]),
        InputExample(texts=["kettlebell Swing", "kettlebell russian swing", "barbell hang Squat snatch"]),
        InputExample(texts=["Row", "Ski", "Hollow rock"]),
        # InputExample(texts=["Run", "Ski", "Farmers Carry"]),
        InputExample(texts=["bear crawl", "Wall walk", "Shuttle run"]),
        InputExample(texts=["GHD", "Sit-up", "air squat"]),
        InputExample(texts=["ski", "row", "Hollow rock"]),
        InputExample(texts=["air squat", "push up", "dumbell clean"]),
        InputExample(texts=["knee raise", "knees to elbows", "burpee"]),
        InputExample(texts=["burpee", "double under", "plank"]),
        InputExample(texts=["turkish get up", "renegade rows", "box jump"]),
        InputExample(texts=["good morning", "back extension", "box step up"]),
        InputExample(texts=["toes to bars", "toes to ring", "dips"]),
        InputExample(texts=["seated leg raise", "V-up", "box jump"]),
        InputExample(texts=["pistol squat", "air squat", "dumbell windmill"]),
        InputExample(texts=["pike push up", "shoulder tap", "push up"]),
        # InputExample(texts=["push jerk", "split jerk", "clean"]),
        # InputExample(texts=["push press", "push jerk", "squat"]),
        # InputExample(texts=["sprint", "weighted run", "lunge"]),
        InputExample(texts=["air squat", "lunge", "carry"]),
        # InputExample(texts=["kettlebell", "dumbell", "barbell"]),
        InputExample(texts=["Goblet squat", "dumbell lunge", "air squat"]),
        InputExample(texts=["pull up", "toes to bar", "sit-up"]),
        InputExample(texts=["double under", "crossover", "push up"]),
        InputExample(texts=["burpee over the bar", "burpee over the rower", "pull over"]),
        InputExample(texts=["Sumo deadlift", "deadlift", "bench press"]),
        # InputExample(texts=["Echo bike", "sprint", "dumbell step up"]),
        InputExample(texts=["knees to elbows", "toes to bar", "plank"]),
        InputExample(texts=["pull up", "pull over", "sumo deadlift high pull"]),
        InputExample(texts=["hang snatch", "hang clean", "Dead hang"]),
        InputExample(texts=["Dead hang", "ring support hold", "sled push"]),
        InputExample(texts=["Box push", "sled push", "push up"]),
        # InputExample(texts=["Box push", "bear crawl", "push up"]),
        InputExample(texts=["pegboard ascents", "pull up", "run"]),
        InputExample(texts=["Medball hanging knee raise", "V-up", "pull up"]),
        InputExample(texts=["Medball hanging knee raise", "GHD hip extension", "goblet squat"]),
        InputExample(texts=["ring dip", "bar dip", "box step up"]),
        InputExample(texts=["dips", "push up", "squat"]),
        InputExample(texts=["bar dip", "ring dip", "barbell"]),
        InputExample(texts=["row", "erg", "pull up"]),
        InputExample(texts=["ski", "run", "rope climb"]),
        InputExample(texts=["bike", "run", "dead hang"]),
        InputExample(texts=["run", "sprint", "good morning"]),
        InputExample(texts=["row", "weighted run(ruck)", "wall walk"]),
        InputExample(texts=["squat", "wall ball shot", "wall ball sit up"]),
        InputExample(texts=["good morning", "wall ball sit up", "wall walk"]),
        InputExample(texts=["Hollow rock", "Superman", "Dumbel clean and jerk"]),
        InputExample(texts=["Plank hold", "Good Morning", "Box Jump"]),
        InputExample(texts=["Rope climb", "Peg board ascents", "Box jump"]),
        InputExample(texts=["Knees to elbows", "Dead hang", "GHD back extension"]),
        InputExample(texts=["dumbell hold", "farmers carry", "Dumbell snatch"]),
        InputExample(texts=["Kettlebell swing", "Dumbell snatch", "pistol squat"]),
        InputExample(texts=["Ring muscle up", "bar muscle up", "sled drag/push"])
    ]

def train_triplet_model(triplets, model_name="all-MiniLM-L6-v2", output_dir="fine_tuned_crossfit_model", epochs=5):
    model = SentenceTransformer(model_name)
    dataloader = DataLoader(triplets, shuffle=True, batch_size=16)

    # ✅ TripletLoss에 margin 추가
    loss = losses.TripletLoss(
        model=model,
        distance_metric=losses.TripletDistanceMetric.EUCLIDEAN,
        triplet_margin=0.7  # 👈 여기서 margin 크기 조절 가능
    )

    model.fit(
        train_objectives=[(dataloader, loss)],
        epochs=epochs,
        warmup_steps=100,
        show_progress_bar=True
    )
    model.save(output_dir)
    print(f"✅ 모델 저장됨: {output_dir}")

# 실행
basic_triplets = generate_triplets(group_to_movements)
hard_triplets = get_hard_triplets()
all_triplets = basic_triplets + hard_triplets

train_triplet_model(all_triplets)
