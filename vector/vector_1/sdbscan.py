import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
import os
import shutil
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# === 1. Load vectors and filenames ===
vector_path = "vector_1/all.npy"
filename_path = "vector_1/all_filenames.txt"
output_base_dir = "vector_1/cluster_files_sdbscan"

vectors = np.load(vector_path)
with open(filename_path, "r") as f:
    filenames = [line.strip() for line in f.readlines()]

# === 2. Shared Nearest Neighbor Matrix (SNN) 계산 ===
k = 40  # number of nearest neighbors
nbrs = NearestNeighbors(n_neighbors=k, metric="euclidean").fit(vectors)
_, knn_indices = nbrs.kneighbors(vectors)

# Shared Neighbors 유사도 행렬
n = len(vectors)
snn_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(i + 1, n):
        shared = len(set(knn_indices[i]) & set(knn_indices[j]))
        snn_matrix[i][j] = shared
        snn_matrix[j][i] = shared

# 거리 행렬로 변환 (shared neighbors가 클수록 거리 작게)
snn_dist_matrix = k - snn_matrix

# === 3. DBSCAN with precomputed distance ===
dbscan = DBSCAN(eps=7, min_samples=5, metric="precomputed")
labels = dbscan.fit_predict(snn_dist_matrix)
unique_labels = sorted(set(labels))

# === 4. PCA (for visualization only) ===
pca = PCA(n_components=0.95)
reduced = pca.fit_transform(vectors)

# === 5. Copy associated text files into cluster folders ===
os.makedirs(output_base_dir, exist_ok=True)
cluster_to_files = {label: [] for label in unique_labels}

for idx, label in enumerate(labels):
    cluster_to_files[label].append(filenames[idx])

for label in unique_labels:
    label_dir = os.path.join(output_base_dir, f"cluster_{label}" if label != -1 else "noise")
    os.makedirs(label_dir, exist_ok=True)
    for full_path in cluster_to_files[label]:
        parts = full_path.replace("\\", "/").split("/")
        source = parts[-2]
        file_name = os.path.splitext(parts[-1])[0]
        source_txt_path = f"../data/crawled_data/{source}/refined/{file_name}.txt"
        target_txt_path = os.path.join(label_dir, f"{file_name}.txt")
        try:
            shutil.copyfile(source_txt_path, target_txt_path)
        except FileNotFoundError:
            print(f"❌ 파일 없음: {source_txt_path}")

# === 6. Plotting with cluster labels ===
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

plt.title("WOD S-DBSCAN Clusters (Shared Neighbors)")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.grid(True)
plt.tight_layout()
plt.show()

# === 7. Top 20 distant points by PC1 ===
pc1_values = reduced[:, 0]
far_indices = np.argsort(-np.abs(pc1_values))[:20]
far_filenames = [filenames[i] for i in far_indices]

# 결과 반환
pd.DataFrame({
    "Index": far_indices,
    "Filename": far_filenames,
    "PC1 Value": pc1_values[far_indices]
})