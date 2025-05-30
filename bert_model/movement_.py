movements = [
    "Row", "Ski", "Bike", "Echo bike", "*erg", "Shuttle(run)", "Run", "Weighted run(Ruck)", "Sprint",
    "Bench press", "Deadlift", "Bodyweight Deadlift", "Sumo deadlift", "Sumo deadlift high pull",
    "Back rack/front rack lunge", "Walking Lunge", "Back Squat", "Front Squat", "Power Clean",
    "Squat Clean", "Hang Power Clean", "Hang Squat Snatch", "Clean and Jerk", "Overhead squat",
    "Power Snatch", "Squat Snatch", "Hang Power Snatch", "Hang Squat Snatch", "Snatch",
    "Shoulder to overhead", "Anchor press", "Push press", "Push Jerk", "Split Jerk", "Jerk",
    "Ground to overhead", "Cluster", "Thruster", "Good Morning",

    "dumbell Renegade rows", "dumbell Overhead walking lunge", "dumbell Clean", "dumbell Squat clean",
    "dumbell Hang clean", "dumbell Hang squat clean", "dumbell Clean and Jerk", "dumbell Snatch",
    "dumbell Squat snatch", "dumbell Hang snatch", "dumbell Hang squat snatch", "dumbell Devil Press", "dumbell Burpee deadlift",
    "Goblet Squat", "dumbell Push press", "dumbell Thruster", "kettlebell Swing", "kettlebell Russian Swing", "dumbell/Kettlebell Lunge",

    "Box step up", "dumbell Step up", "Box Jump", "Burpee Box Jump", "Box Jump over", "Burpee Box Jump over",
    "Burpee", "burpee over the dumbell", "burpee over the rower", "burpee over the bar",
    "bar facing burpee", "burpee to plate", "burpee to target", "Air squat", "Medicine ball squat",
    "GHD back extension", "Sit-up", "GHD Sit-up", "Wall ball sit up", "Wall ball shot",
    "Medicine ball clean", "Pistol squat", "jump squat", "Dips", "Frankenstein Front Squat",

    "Rope climb", "legless rope climb", "Bear Crawl", "Bar Muscle up", "Strict Ring Muscle up",
    "Ring Muscle up", "Ring support hold", "Pull over", "Toes to bar", "Strict Toes to bar",
    "Pull up", "Strict Pull up", "Jumping pull up", "Chest to bar pull up", "Strict Chest to bar pull up",
    "Burpee Pull up", "Weighted Pull up", "Peg board ascents", "Bar dip", "Ring dip",
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

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(movements)

scaler = StandardScaler()
embeddings = scaler.fit_transform(embeddings)

pca = PCA(n_components=2)
reduced = pca.fit_transform(embeddings)

# Clustering using KMeans
n_clusters = 10
kmeans = KMeans(n_clusters=n_clusters, random_state=10)
labels = kmeans.fit_predict(embeddings)

# Visualize the clustering result
plt.figure(figsize=(20, 15))
colors = plt.cm.get_cmap("tab10", n_clusters)

for label in range(n_clusters):
    idxs = np.where(labels == label)[0]
    plt.scatter(reduced[idxs, 0], reduced[idxs, 1], label=f"Cluster {label}", alpha=0.5)
    for i in idxs:
        plt.text(reduced[i, 0], reduced[i, 1], movements[i], fontsize=10, alpha=0.6)

plt.title("Movement Clusters (KMeans + PCA)")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

clusters = defaultdict(list)
for i, label in enumerate(labels):
    clusters[label].append(movements[i])

cluster_text = ""
for cluster_id in sorted(clusters.keys()):
    cluster_text += f"Cluster {cluster_id}:\n" + "\n".join(f"  - {movement}" for movement in clusters[cluster_id]) + "\n\n"

# Save to text file
file_path = "movement_clusters_kmeans.txt"
with open(file_path, "w") as f:
    f.write(cluster_text)
