import argparse
import requests
import json
import time
import re
import threading
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class WebScraper:
    def __init__(self, base_url, depth_limit, threads, delay, user_agent, vectorize, logger=None, log_queue=None):
        self.base_url = base_url
        self.depth_limit = depth_limit
        
        self.domain = urlparse(base_url).netloc
        self.vectorize = vectorize
        self.max_threads = threads
        self.request_delay = delay
        self.queue = deque([(self.base_url, 0, ["Home"])])
        self.visited_urls = {self.base_url}
        self.scraped_data = []
        self.navigation_log = []
        self.data_lock = threading.Lock()
        self.user_agent = user_agent
        self.robot_parser = RobotFileParser()

        self.logger = logger
        self.log_queue = log_queue

        robots_url = urljoin(self.base_url, 'robots.txt')
        self.log(f"🤖 Reading robots.txt from: {robots_url}")
        try:
            self.robot_parser.set_url(robots_url)
            self.robot_parser.read()
        except Exception as e:
            self.log(f"Could not read robots.txt: {e}")

        self.embedding_model = None
        if self.vectorize:
            self.log("🧠 Initializing sentence-transformer model...")
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.log("✅ Model loaded.")

    def log(self, message):
        if self.logger:
            self.logger(message)
        elif self.log_queue:
            self.log_queue.put(message)
        else:
            print(message)

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        if parsed_url.netloc != self.domain:
            return False
        excluded = re.compile(r'.*\.(jpg|jpeg|png|gif|pdf|zip|mp3|mp4|css|js)$', re.I)
        if excluded.match(parsed_url.path) or parsed_url.scheme not in ['http', 'https'
                                                                        ]:
            return False
        return True

    def chunk_and_clean_text(self, soup):
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        text = soup.get_text(separator='\n', strip=True)
        chunks = [chunk.strip() for chunk in re.split(r'\n\s*\n', text) if chunk.strip()]
        return chunks

    def _process_url(self, url_info):
        current_url, current_depth, current_path = url_info
        path_str = " -> ".join(current_path)

        if not self.robot_parser.can_fetch(self.user_agent, current_url):
            self.log(f"🚫 Denied by robots.txt: {current_url}")
            with self.data_lock:
                self.navigation_log.append(f"{path_str} ==> denied by robots.txt")
            return []

        time.sleep(self.request_delay)

        try:
            self.log(f"Scraping [Depth {current_depth}]: {path_str}")
            response = requests.get(current_url, timeout=10, headers={'User-Agent': self.user_agent})
            response.raise_for_status()

            if 'text/html' not in response.headers.get('Content-Type', ''):
                with self.data_lock:
                    self.navigation_log.append(f"{path_str} ==> skipped (not HTML)")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            text_chunks = self.chunk_and_clean_text(soup)
            if not text_chunks: return []

            page_content = {'url': current_url, 'path': path_str, 'chunks': []}
            if self.vectorize and self.embedding_model:
                embeddings = self.embedding_model.encode(text_chunks, convert_to_tensor=False)
                for i, chunk in enumerate(text_chunks):
                    page_content['chunks'].append({'text': chunk, 'vector': embeddings[i].tolist()})
            else:
                for chunk in text_chunks:
                    page_content['chunks'].append({'text': chunk})

            new_links = []
            if current_depth < self.depth_limit:
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(current_url, link.get('href'))
                    full_url = urlparse(full_url)._replace(fragment="").geturl()
                    new_links.append((full_url, link.get_text(strip=True) or "link"))

            with self.data_lock:
                self.scraped_data.append(page_content)
                self.navigation_log.append(f"{path_str} ==> scraped")
            return new_links

        except requests.exceptions.HTTPError as e:
            self.log(f"HTTP Error for {current_url}: {e}")
            with self.data_lock: self.navigation_log.append(f"{path_str} ==> failed (HTTP Error: {e.response.status_code})")
        except requests.exceptions.RequestException as e:
            self.log(f"Error fetching {current_url}: {e}")
            with self.data_lock: self.navigation_log.append(f"{path_str} ==> failed ({e})")
        return []

    def crawl(self):
        self.log(f"🚀 Starting crawl with {self.max_threads} threads.")
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            while self.queue:
                current_url_info = self.queue.popleft()
                future = executor.submit(self._process_url, current_url_info)
                try:
                    new_links = future.result()
                    _, current_depth, current_path = current_url_info
                    if current_depth < self.depth_limit:
                        for url, text in new_links:
                            with self.data_lock:
                                if self.is_valid_url(url) and url not in self.visited_urls:
                                    self.visited_urls.add(url)
                                    self.queue.append((url, current_depth + 1, current_path + [text]))
                except Exception as e:
                    self.log(f"A worker thread failed: {e}")
        self.log("✅ Crawl finished!")

    def get_results(self):
        """Returns the results as strings for UI download."""
        json_output = json.dumps(self.scraped_data, indent=4, ensure_ascii=False)
        log_output = "\n".join(self.navigation_log)
        return json_output, log_output