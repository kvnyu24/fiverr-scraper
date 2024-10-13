# scraper.py

import sqlite3
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import setup_logger

logger = setup_logger("scraper")

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
        logger.info("Database table created or already exists.")

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logger.info("Web driver setup completed.")

    def scrape_gig_data(self, num_pages=5):
        for page in range(1, num_pages + 1):
            url = f"{self.base_url}&page={page}"
            self.driver.get(url)
            time.sleep(3)  # Allow time for the page to load
            logger.info(f"Scraping page {page}")

            gigs = self.driver.find_elements(By.CLASS_NAME, 'gig-card-layout')
            for gig in gigs:
                try:
                    title = gig.find_element(By.CLASS_NAME, 'gig-title').text.strip()
                except Exception as e:
                    title = ""
                    logger.warning(f"Failed to scrape title: {e}")
                try:
                    description = gig.find_element(By.CLASS_NAME, 'gig-description').text.strip()
                except Exception as e:
                    description = ""
                    logger.warning(f"Failed to scrape description: {e}")
                self.store_data(title, description)

    def store_data(self, title, description):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO gigs (title, description) VALUES (?, ?)', (title, description))
        self.conn.commit()
        logger.info(f"Stored gig: {title[:50]}...")

    def close_connection(self):
        self.conn.close()
        self.driver.quit()
        logger.info("Database connection closed and web driver quit.")

