import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import os
import shutil
import pandas as pd

# === 1. Load vectors and filenames ===
source_name = "millburn"
vector_path = f"{source_name}.npy"
filename_path = f"{source_name}_filenames.txt"
output_base_dir = f"cluster_files_kmeans"

vectors = np.load(vector_path)
with open(filename_path, "r") as f:
    filenames = [line.strip() for line in f.readlines()]

# === 2. StandardScaler 적용 ===
scaler = StandardScaler()
vectors_scaled = scaler.fit_transform(vectors)

# === 3. KMeans 클러스터링 ===
n_clusters = 4  # 원하는 클러스터 수

import random
random_state = random.randint(0, 100000)
print(f"rand state: {random_state}")
random_state = 11390

kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=random_state)
labels = kmeans.fit_predict(vectors_scaled)
unique_labels = sorted(set(labels))

score = silhouette_score(vectors_scaled, labels)
print(f"siluette score: {score:.4f}")

# for k in range(2, 11):
#     labels = KMeans(n_clusters=k, random_state=42).fit_predict(vectors_scaled)
#     score = silhouette_score(vectors_scaled, labels)
#     print(f"k={k}, Silhouette Score={score:.4f}")

# === 4. PCA for 시각화 ===
pca = PCA(n_components=2)
reduced = pca.fit_transform(vectors_scaled)

output_txt = output_base_dir + '/txt'
output_json = output_base_dir + '/json'

# === 5. 클러스터별 텍스트 파일 복사 ===
os.makedirs(output_base_dir, exist_ok=True)
os.makedirs(output_txt, exist_ok=True)
os.makedirs(output_json, exist_ok=True)
cluster_to_files = {label: [] for label in unique_labels}
for idx, label in enumerate(labels):
    cluster_to_files[label].append(filenames[idx])

for label in unique_labels:
    label_dir = os.path.join(output_txt, f"cluster_{label}")
    os.makedirs(label_dir, exist_ok=True)

    for fname in cluster_to_files[label]:
        file_base = os.path.splitext(fname)[0]
        source_txt_path = f"../../data/crawled_data/{source_name}/refined/{file_base}.txt"
        target_txt_path = os.path.join(label_dir, f"{file_base}.txt")
        try:
            shutil.copyfile(source_txt_path, target_txt_path)
        except FileNotFoundError:
            print(f"❌ 파일 없음: {source_txt_path}")

for label in unique_labels:
    label_dir = os.path.join(output_json, f"cluster_{label}")
    os.makedirs(label_dir, exist_ok=True)

    for fname in cluster_to_files[label]:
        file_base = os.path.splitext(fname)[0]
        source_txt_path = f"../../data/normed_data/{source_name}/{file_base}.json"
        target_txt_path = os.path.join(label_dir, f"{file_base}.json")
        try:
            shutil.copyfile(source_txt_path, target_txt_path)
        except FileNotFoundError:
            print(f"❌ 파일 없음: {source_txt_path}")

# === 6. 시각화 ===
plt.figure(figsize=(8, 6))
plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap='tab10', alpha=0.7)

# 클러스터 중심 표시
for label in unique_labels:
    idxs = np.where(labels == label)[0]
    if len(idxs) == 0:
        continue
    center_x = np.mean(reduced[idxs, 0])
    center_y = np.mean(reduced[idxs, 1])
    plt.text(center_x, center_y, f"Cluster {label}", fontsize=10, fontweight='bold', ha='center')

plt.title(f"{source_name.capitalize()} KMeans Clusters")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.grid(True)
plt.tight_layout()
plt.show()

# === 7. 가장 멀리 떨어진 20개 WOD 확인 ===
pc1_values = reduced[:, 0]
far_indices = np.argsort(-np.abs(pc1_values))[:20]

df = pd.DataFrame({
    "Index": far_indices,
    "Filename": [filenames[i] for i in far_indices],
    "PC1 Value": pc1_values[far_indices]
})
print(df.to_string(index=False))