# Fiverr Gig Scraper and Common Request Analyzer

import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class FiverrScraper:
    def __init__(self, base_url, db_name='fiverr_gigs.db'):
        self.base_url = base_url
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_table()
        self.setup_driver()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gigs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT
            )
        ''')
        self.conn.commit()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_gig_data(self, num_pages=5):
        for page in range(1, num_pages + 1):
            url = f"{self.base_url}&page={page}"
            self.driver.get(url)
            time.sleep(3)  # Allow time for the page to load

            gigs = self.driver.find_elements(By.CLASS_NAME, 'gig-card-layout')
            for gig in gigs:
                try:
                    title = gig.find_element(By.CLASS_NAME, 'gig-title').text.strip()
                except:
                    title = ""
                try:
                    description = gig.find_element(By.CLASS_NAME, 'gig-description').text.strip()
                except:
                    description = ""
                self.store_data(title, description)

    def store_data(self, title, description):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO gigs (title, description) VALUES (?, ?)', (title, description))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()
        self.driver.quit()

class FiverrAnalyzer:
    def __init__(self, db_name='fiverr_gigs.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)

    def load_data(self):
        query = "SELECT description FROM gigs WHERE description != ''"
        df = pd.read_sql_query(query, self.conn)
        return df['description']

    def perform_clustering(self, descriptions, num_clusters=5):
        if descriptions.empty:
            print("No data available for clustering.")
            return
        
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        
        if tfidf_matrix.shape[1] == 0:
            print("Empty vocabulary; perhaps the documents only contain stop words.")
            return
        
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(tfidf_matrix)
        
        clusters = kmeans.predict(tfidf_matrix)
        
        for i in range(num_clusters):
            print(f"\nCluster {i+1}:")
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

if __name__ == '__main__':
    # Step 1: Scrape Fiverr data and save it into a local SQLite database
    base_url = "https://www.fiverr.com/search/gigs?query=your_keyword_here"
    scraper = FiverrScraper(base_url)
    scraper.scrape_gig_data(num_pages=5)  # Scrape 5 pages as an example
    scraper.close_connection()
    
    # Step 2: Load scraped data and perform clustering analysis
    analyzer = FiverrAnalyzer()
    descriptions = analyzer.load_data()
    analyzer.perform_clustering(descriptions, num_clusters=5)
    analyzer.close_connection()