# Provided flat movement list with updated barbell/dumbbell labels
movements = [
    "Row", "Ski", "Bike", "Echo bike", "*erg", "Shuttle(run)", "Run", "Weighted run(Ruck)", "Sprint",
    "barbell Bench press", "barbell Deadlift", "barbell Bodyweight Deadlift", "barbell Sumo deadlift", "barbell Sumo deadlift high pull",
    "barbell Back rack/front rack lunge", "Walking Lunge", "barbell Back Squat", "barbell Front Squat", "barbell Power Clean",
    "barbell Squat Clean", "barbell Hang Power Clean", "barbell Hang Squat Snatch", "barbell Clean and Jerk", "barbell Overhead squat",
    "barbell Power Snatch", "barbell Squat Snatch", "barbell Hang Power Snatch", "barbell Hang Squat Snatch", "barbell Snatch",
    "barbell Shoulder to overhead", "barbell Anchor press", "barbell Push press", "barbell Push Jerk", "barbell Split Jerk", "barbell Jerk",
    "barbell Ground to overhead", "barbell Cluster", "barbell Thruster", "Good Morning",

    "dumbell Renegade rows", "dumbell Overhead walking lunge", "dumbell Clean", "dumbell Squat clean",
    "dumbell Hang clean", "dumbell Hang squat clean", "dumbell Clean and Jerk", "dumbell Snatch",
    "dumbell Squat snatch", "dumbell Hang snatch", "dumbell Hang squat snatch", "dumbell Devil Press", "dumbell Burpee deadlift",
    "Goblet Squat", "dumbell Push press", "dumbell Thruster", "kettlebell Swing", "kettlebell Russian Swing", "dumbell/Kettlebell Lunge",
    "dumbell/Kettlebell Walking Lunge", "dumbell/Kettlebell Overhead walk", "dumbell Turkish get up", "dumbell Windmill", "Overhead Plate lunge",

    "Box step up", "dumbell Step up", "Box Jump", "Burpee Box Jump", "Box Jump over", "Burpee Box Jump over",
    "Burpee", "burpee over the dumbell", "burpee over the rower", "burpee over the bar",
    "bar facing burpee", "burpee to plate", "burpee to target", "Air squat", "Medicine ball squat",
    "Hand-release push up", "Push up", "Ring push up", "Pike push up", "Lunge", "Walking Lunge",
    "Skipping", "Shoulder tap", "Double under", "Crossover", "Reverse Double under", "GHD hip extension",
    "GHD back extension", "Sit-up", "GHD Sit-up", "Wall ball sit up", "Wall ball shot",
    "Medicine ball clean", "Pistol squat", "jump squat", "Dips", "barbell Frankenstein Front Squat",

    "Rope climb", "legless rope climb", "Bear Crawl", "Bar Muscle up", "Strict Ring Muscle up",
    "Ring Muscle up", "Ring support hold", "Pull over", "Toes to bar", "Strict Toes to bar",
    "Toes to ring", "Knee raise", "Knees to elbows", "Med ball hanging knee raise", "Ring row",
    "Pull up", "Strict Pull up", "Jumping pull up", "Chest to bar pull up", "Strict Chest to bar pull up",
    "Burpee Pull up", "Weighted Pull up", "Peg board ascents", "Bar dip", "Ring dip",
    "Wall-facing handstand shoulder tap", "Handstand walk", "Handstand Hold", "Handstand push up",
    "Strict handstand push up", "Wall facing strict handstand push up", "Wall walk",
    "Sled drag/push", "Box (sled) push", "Dead Hang", "Goblet Carry", "Farmers Carry",
    "dumbell Hold", "dumbell Front rack hold", "Plank Hold", "V-up", "Superman", "L-sit hold",
    "Hollow rock", "Seated leg raise", "Flutter kick", "Russian twist", "Back extension"
]

from sentence_transformers import SentenceTransformer
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import defaultdict

# Load fine-tuned model
model = SentenceTransformer("fine_tuned_crossfit_model/")

# Generate embeddings
embeddings = model.encode(movements)

scaler = StandardScaler()
embeddings = scaler.fit_transform(embeddings)

# Dimensionality reduction for visualization
pca = PCA(n_components=2)
reduced = pca.fit_transform(embeddings)

# Clustering using KMeans
n_clusters = 10  # 원하는 클러스터 수로 조절 가능
kmeans = KMeans(n_clusters=n_clusters, random_state=10)
labels = kmeans.fit_predict(embeddings)

# Visualize the clustering result
plt.figure(figsize=(14, 10))
colors = plt.cm.get_cmap("tab10", n_clusters)

for label in range(n_clusters):
    idxs = np.where(labels == label)[0]
    plt.scatter(reduced[idxs, 0], reduced[idxs, 1], label=f"Cluster {label}", alpha=0.5)
    for i in idxs:
        plt.text(reduced[i, 0], reduced[i, 1], movements[i], fontsize=7, alpha=0.6)

plt.title("Movement Clusters with Barbell/Dumbell Labels (KMeans + PCA)")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

clusters = defaultdict(list)
for i, label in enumerate(labels):
    clusters[label].append(movements[i])

# Format clustering results as text
cluster_text = ""
for cluster_id in sorted(clusters.keys()):
    cluster_text += f"Cluster {cluster_id}:\n" + "\n".join(f"  - {movement}" for movement in clusters[cluster_id]) + "\n\n"

# Save to text file
file_path = "movement_clusters_kmeans.txt"
with open(file_path, "w") as f:
    f.write(cluster_text)
