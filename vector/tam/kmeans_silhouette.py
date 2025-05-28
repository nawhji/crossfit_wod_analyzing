import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import random

# === 데이터 불러오기 ===
source_name = "tam"
vector_path = f"{source_name}.npy"
filename_path = f"{source_name}_filenames.txt"

vectors = np.load(vector_path)
with open(filename_path, "r") as f:
    filenames = [line.strip() for line in f.readlines()]

# === 스케일링 ===
scaler = StandardScaler()
vectors_scaled = scaler.fit_transform(vectors)

# === 클러스터 수에 따른 실루엣 스코어 평균 계산 ===
print("n_clusters | Silhouette Score (mean of 10 runs)")
print("-----------------------------------------------")

for k in range(2, 12):
    scores = []
    for _ in range(10):
        random_state = random.randint(0, 100000)
        kmeans = KMeans(n_clusters=k, init='k-means++', random_state=random_state)
        labels = kmeans.fit_predict(vectors_scaled)

        if len(set(labels)) > 1:  # 클러스터가 최소 2개여야 계산 가능
            score = silhouette_score(vectors_scaled, labels)
            scores.append(score)

    if scores:
        mean_score = np.mean(scores)
        print(f"{k:>10} | {mean_score:.4f}")
    else:
        print(f"{k:>10} | (실루엣 계산 불가)")
