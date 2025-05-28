import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
import os
import shutil

# === 1. Load vectors and filenames ===
vector_path = "vector_1/all.npy"
filename_path = "vector_1/all_filenames.txt"
output_base_dir = "vector_1/cluster_files_dbscan"

vectors = np.load(vector_path)
with open(filename_path, "r") as f:
    filenames = [line.strip() for line in f.readlines()]

# === 2. DBSCAN clustering ===
pca = PCA(n_components=2)
reduced = pca.fit_transform(vectors)

dbscan = DBSCAN(eps=0.9, min_samples=7)
labels = dbscan.fit_predict(vectors)
unique_labels = sorted(set(labels))

# === 3. Copy associated text files into cluster folders ===
os.makedirs(output_base_dir, exist_ok=True)
cluster_to_files = {label: [] for label in unique_labels}

for idx, label in enumerate(labels):
    cluster_to_files[label].append(filenames[idx])

for label in unique_labels:
    label_dir = os.path.join(output_base_dir, f"cluster_{label}" if label != -1 else "noise")
    os.makedirs(label_dir, exist_ok=True)
    for full_path in cluster_to_files[label]:
        # Example: ../data/normed_data/calgary\18_2.json
        parts = full_path.replace("\\", "/").split("/")
        source = parts[-2]
        file_name = os.path.splitext(parts[-1])[0]
        source_txt_path = f"../data/crawled_data/{source}/refined/{file_name}.txt"
        target_txt_path = os.path.join(label_dir, f"{file_name}.txt")
        try:
            shutil.copyfile(source_txt_path, target_txt_path)
        except FileNotFoundError:
            print(f"❌ 파일 없음: {source_txt_path}")

# === 4. Plotting with cluster labels ===
plt.figure(figsize=(8, 6))
plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap='tab10', alpha=0.7)

for label in unique_labels:
    idxs = np.where(labels == label)[0]
    if len(idxs) == 0:
        continue
    center_x = np.mean(reduced[idxs, 0])
    center_y = np.mean(reduced[idxs, 1])
    label_text = f"Cluster {label}" if label != -1 else "Noise"
    plt.text(center_x, center_y, label_text, fontsize=10, fontweight='bold', color='black', ha='center')

plt.title("WOD DBSCAN Clusters")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.grid(True)
plt.tight_layout()
plt.show()

# === 5. Top 20 distant points by PC1 ===
pc1_values = reduced[:, 0]
far_indices = np.argsort(-np.abs(pc1_values))[:20]
far_filenames = [filenames[i] for i in far_indices]

import pandas as pd

df = pd.DataFrame({
    "Index": far_indices,
    "Filename": [filenames[i] for i in far_indices],
    "PC1 Value": pc1_values[far_indices]
})

print(df.to_string(index=False))