# analyzer.py

import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import logging
from utils.logger import setup_logger

logger = setup_logger("analyzer")

class FiverrAnalyzer:
    def __init__(self, db_name='fiverr_gigs.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        logger.info("Database connection established.")

    def load_data(self):
        query = "SELECT description FROM gigs WHERE description != ''"
        df = pd.read_sql_query(query, self.conn)
        logger.info(f"Loaded {len(df)} descriptions from database.")
        return df['description']

    def perform_clustering(self, descriptions, num_clusters=5):
        if descriptions.empty:
            logger.warning("No data available for clustering.")
            return
        
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        
        if tfidf_matrix.shape[1] == 0:
            logger.warning("Empty vocabulary; perhaps the documents only contain stop words.")
            return
        
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(tfidf_matrix)
        
        clusters = kmeans.predict(tfidf_matrix)
        
        for i in range(num_clusters):
            logger.info(f"Cluster {i+1} contains {sum(clusters == i)} gigs.")
            cluster_descriptions = [desc for idx, desc in enumerate(descriptions) if clusters[idx] == i]
            for description in cluster_descriptions[:3]:  # Print top 3 descriptions in the cluster
                print(description[:200], '...')
        
        plt.figure(figsize=(10, 6))
        plt.hist(clusters, bins=num_clusters, rwidth=0.8)
        plt.xlabel('Cluster ID')
        plt.ylabel('Number of Gigs')
        plt.title('Distribution of Fiverr Gigs in Clusters')
        plt.show()

    def close_connection(self):
        self.conn.close()
        logger.info("Database connection closed.")

