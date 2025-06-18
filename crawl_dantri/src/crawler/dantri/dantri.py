#Định nghĩa lớp Dantri, kế thừa từ BaseCrawler, chứa toàn bộ logic crawl bài viết từ Dân Trí.

import time
from bs4 import Tag
from tqdm import tqdm
from typing import List
from slugify import slugify
from datetime import datetime
from urllib.parse import urljoin
from collections import defaultdict
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from config import Config
from src.crawler.base import BaseCrawler, News


class Dantri(BaseCrawler):

    def __init__(self, *args, **kwargs):
        super().__init__(parent_url="https://dantri.com.vn/", *args, **kwargs)

    #Lọc URL hợp lệ
    def _is_valid_article_url(self, url: str) -> bool:
        return (
            url.endswith(".htm")
            and not any(x in url.lower() for x in ["video", "gallery", "dnews", "infographic", "#"])
        )
    
    # Selenium Headless + Scroll trang với trang tin-moi-nhat
    def _scrape_latest_news_from_homepage_selenium(self, max_scroll: int = 12) -> List[str]:
        with open("crawl_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[INFO] Crawling Tin Mới Nhất with Selenium scroll x{max_scroll}...\n")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get("https://dantri.com.vn/tin-moi-nhat.htm")
            for i in range(max_scroll):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print(f"[INFO] Scrolled {i+1}/{max_scroll}")
                time.sleep(2)

            #HTML Parsing từ nội dung sau khi scroll
            soup = BeautifulSoup(driver.page_source, "html.parser")
            article_tags = soup.select("article.article-item a[href$='.htm']")

            raw_links = [
                urljoin("https://dantri.com.vn/", a["href"].split("#")[0])
                for a in article_tags if a.get("href")
            ]

            valid_links = [
                link for link in raw_links if self._is_valid_article_url(link)
            ]

            unique_links = list(dict.fromkeys(valid_links))
            with open("crawl_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[INFO] Found {len(unique_links)} unique links from Tin Mới Nhất.\n")
            return unique_links

        finally:
            driver.quit()

    #Trích xuất nội dung bài báo
    def _scrape_news(self, url: str, *args, **kwargs):
        news_soup = self._fetch(url, *args, **kwargs)
        if not news_soup or not news_soup.text.strip():
            print(f"[WARN] Empty or invalid soup for: {url}")
            return None

        title = news_soup.find("h1", class_="title-page detail")
        author_name = news_soup.select_one("div.author-wrap > div.author-meta > div.author-name")
        author_time = news_soup.select_one("div.author-wrap > div.author-meta > time.author-time")
        div_content = news_soup.select_one("div.singular-content")

        if all([title, author_name, author_time, div_content]):
            return News(
                title=title.text.strip(),
                author=author_name.text.strip(),
                created_at=datetime.strptime(author_time.get("datetime"), "%Y-%m-%d %H:%M"),
                content=div_content.text.strip(),
                url=url,
            )
        return None

    #Đệ quy qua phân trang chuyên mục
    def _scrape_topic(self, url: str, n_th_page: int = 1, *args, **kwargs):
        time.sleep(Config.SLEEP_TIME)
        if n_th_page > kwargs.get("max_pagination", Config.MAX_PAGINATION):
            return []

        paged_url = url if n_th_page == 1 else f"{url}/p{n_th_page}"
        soup = self._fetch(paged_url, *args, **kwargs)
        if not soup:
            return []

        article_tags = soup.select("article.article-item a[href$='.htm']")
        news_links = [
            urljoin(self.parent_url, a["href"].split("#")[0])
            for a in article_tags if a.get("href") and self._is_valid_article_url(a["href"])
        ]

        if news_links:
            news_links += self._scrape_topic(url, n_th_page + 1, *args, **kwargs)
        return news_links

    #Tổng hợp mọi kỹ thuật crawl
    def crawl(self, max_pagination: int = 5, link_only: bool = False, *args, **kwargs) -> List[News] | List[str]:
        news_links = []

        homepage_links = self._scrape_latest_news_from_homepage_selenium(max_scroll=12)
        print(f"[INFO] Collected {len(homepage_links)} links from latest news")

        if link_only:
            news_links.extend(homepage_links)
        else:
            for link in (pbar := tqdm(homepage_links, desc="Crawling latest news")):
                time.sleep(Config.SLEEP_TIME)
                result = self._scrape_news(link)
                if result:
                    news_links.append(result)

        main_page_soup = self._fetch(self.parent_url)
        nav_bar_tag = main_page_soup.select_one("nav.menu.container")
        assert nav_bar_tag is not None, "Cannot find navigation bar"

        li_tags = nav_bar_tag.select("li.has-child")
        assert len(li_tags) > 0, "Cannot find any topics"

        topics = defaultdict(list)
        for li in li_tags:
            main_topic = li.find("a")
            topic_key = slugify(main_topic.text.strip())
            submenu = li.find("ol", class_="submenu")
            if submenu:
                for a_tag in submenu.find_all("a", href=True):
                    full_url = urljoin(self.parent_url, a_tag["href"])
                    topics[topic_key].append(full_url)

        print(f"There are {len(topics)} main topics. Start scraping topic links ...")

        topic_links = []
        for key, val in (pbar := tqdm(topics.items())):
            pbar.set_description(f"Processing {key}")
            for v in val:
                topic_links += self._scrape_topic(v, max_pagination=max_pagination, pbar=pbar)
            pbar.set_postfix(n_news=len(topic_links))
            pbar.set_description(f"Sleeping for {Config.SLEEP_TIME}s ...")
            time.sleep(Config.SLEEP_TIME)

        topic_links = list(dict.fromkeys(topic_links))

        if link_only:
            return news_links + topic_links

        print("Start crawling content from topic links ...")
        for link in (pbar := tqdm(topic_links)):
            time.sleep(Config.SLEEP_TIME)
            result = self._scrape_news(link)
            if result:
                news_links.append(result)

        return news_links

