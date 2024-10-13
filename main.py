# Fiverr Gig Scraper and Common Request Analyzer

# Project Structure:
# 1. scraper.py: Contains the FiverrScraper class to scrape gig data.
# 2. analyzer.py: Contains the FiverrAnalyzer class to analyze and cluster the data.
# 3. main.py: Entry point of the project.
# 4. utils/logger.py: Contains a logging setup for the project.


# main.py

from scraper import FiverrScraper
from analyzer import FiverrAnalyzer

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