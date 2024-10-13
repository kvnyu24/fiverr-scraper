# Fiverr Gig Scraper and Common Request Analyzer

# Project Structure:
# 1. scraper.py: Contains the FiverrScraper class to scrape gig data.
# 2. analyzer.py: Contains the FiverrAnalyzer class to analyze and cluster the data.
# 3. main.py: Entry point of the project.
# 4. utils/logger.py: Contains a logging setup for the project.

# scraper.py

import sqlite3
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import setup_logger
import random
import requests

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
        user_agent = self.get_random_user_agent()
        chrome_options.add_argument(f"--user-agent={user_agent}")

        # Setting up a proxy to circumvent potential blocks
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        # Setting up a proxy to circumvent potential blocks
        proxy_address = self.get_random_proxy()  # Random proxy for each session
        chrome_options.add_argument(f"--proxy-server={proxy_address}")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logger.info("Web driver setup completed with user agent and proxy.")

    def get_random_user_agent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
        ]
        return random.choice(user_agents)

    def get_random_proxy(self):
        # Placeholder for a proxy list, ideally use a rotating proxy service
        proxies = [
            "192.158.29.25:8080",
            "185.37.211.222:5030",
            "89.36.166.54:3128",
            "51.79.50.31:9300"
        ]
        return random.choice(proxies)

    def scrape_gig_data(self, num_pages=5):
        for page in range(1, num_pages + 1):
            url = f"{self.base_url}&page={page}"
            logger.info(f"Accessing URL: {url}")
            self.driver.get(url)
            time.sleep(5)  # Allow more time for the page to load

            page_source = self.driver.page_source
            with open(f'page_source_page_{page}.html', 'w', encoding='utf-8') as f:
                f.write(page_source)

            if "captcha" in page_source.lower() or "needs a human touch" in page_source.lower():
                logger.warning("Captcha or human verification detected. Switching proxy and retrying.")
                self.setup_driver()  # Reset driver with a new proxy and user agent
                continue

            logger.debug(f"Fetched HTML content for page {page}: {page_source[:500]}...")  # Log part of the HTML content

            gigs = self.driver.find_elements(By.CLASS_NAME, 'gig-wrapper')
            logger.info(f"Found {len(gigs)} gigs on page {page}.")

            if not gigs:
                logger.warning(f"No gigs found on page {page}. Check if the class names are correct or if the content is being dynamically loaded.")

            for gig in gigs:
                try:
                    title = gig.find_element(By.CSS_SELECTOR, 'a[aria-label="Go to gig"] p').text.strip()
                    logger.debug(f"Scraped title: {title}")
                except Exception as e:
                    title = ""
                    logger.warning(f"Failed to scrape title: {e}")
                try:
                    description_element = gig.find_element(By.CLASS_NAME, 'gig-description')
                    description = description_element.text.strip() if description_element else ""
                    logger.debug(f"Scraped description: {description}")
                except Exception as e:
                    description = ""
                    logger.warning(f"Failed to scrape description: {e}")
                self.store_data(title, description)

    def store_data(self, title, description):
        if title or description:  # Only store if there's valid data
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO gigs (title, description) VALUES (?, ?)', (title, description))
            self.conn.commit()
            logger.info(f"Stored gig: {title[:50]}...")
        else:
            logger.info("Skipped storing empty gig data.")

    def close_connection(self):
        self.conn.close()
        self.driver.quit()
        logger.info("Database connection closed and web driver quit.")