# Box to Box: Analyzing CrossFit WOD Variability with Structured Embeddings

Hi, thanks for your interest in this project.
This repository analyzes CrossFit WOD (Workout of the Day) variability using structured JSON embeddings and KMeans clustering.

Here's the structure of this repository,
and if you want to know the details, check my `report/Analyzing Crossfit WOD Variability with Structured Embeddings.pdf` !

📁 bert_model/                    
ㄴ 📁 checkpoints/                              
ㄴ 📁 fine_tuned_crossfit_model/                    # model is here
ㄴ bert_finetune.py                            
ㄴ final.png                                        # how this BERT model finetuned! (result graph, with PCA)
ㄴ final.txt 
ㄴ movement_.py 
ㄴ movement_clusters_kmeans.py                      # to test finetuned BERT performance(result)
ㄴ movement.py                                      # to test finetuned BERT performance

📁 data/                                           # WOD text data and structured JSON files
ㄴ 📁 crawled_data/                                # Raw workout texts collected from websites
ㄴ 📁 normed_data/                                 # Cleaned and normalized WOD data in JSON format
ㄴ check.py                                         # Script for inspecting JSON formatting or errors
ㄴ norm.py                                          # JSON normalization and cleaning logic (without API key!!)

📁 vector/ # Vectorized WOD data per CrossFit gym (box)
ㄴ 📁 (box name)/
   ㄴ 📁 cluster_analysis_result                   # Summaries about clusters
   ㄴ 📁 cluster_files_kmeans                      # file organized for easy analysis
      ㄴ 📁 json
      ㄴ 📁 txt
   ㄴ cluster_analysis.py
   ㄴ (box name)_filenames.txt                     # filename organized for cluster result
   ㄴ (box name).csv                               # vector
   ㄴ (box name).npy                               # vector
   ㄴ figure.png                                   # cluster result(graph, 2 dim)
   ㄴ kmeans.py
   ㄴ vectorize.py
ㄴ result.zip

📁 report/ # You can check here my report and poster!
📄 README.md