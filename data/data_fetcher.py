import requests
import json
import os
import logging
from datetime import datetime
from bs4 import BeautifulSoup


class DataFetcher:
    """
    Class to fetch and manage data about Swiss popular initiatives.
    """

    def __init__(self, cache_duration=86400):  # Cache for 24 hours by default
        """
        Initialize the DataFetcher.

        Args:
            cache_duration (int): Duration in seconds for which to cache data.
        """
        self.cache_duration = cache_duration
        self.cache_file = os.path.join("data", "cache", "initiatives_data.json")
        self.logger = self._setup_logger()
        self.initiatives_data = self._load_data()

    def _setup_logger(self):
        """
        Set up logging for the data fetcher.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _load_data(self):
        """
        Load data from cache if available and not expired, otherwise fetch from source.

        Returns:
            dict: Dictionary containing initiative data.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as file:
                    cache_data = json.load(file)
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                current_time = datetime.now()
                # Check if cache is still valid
                if (current_time - cache_time).total_seconds() < self.cache_duration:
                    self.logger.info("Loading initiatives data from cache")
                    initiatives = cache_data.get('data', {}).get('initiatives', [])
                    # If the cached initiatives list is not empty, use it; otherwise fetch new data.
                    if initiatives:
                        return cache_data.get('data', {})
                    else:
                        self.logger.warning("Cached initiatives data is empty, fetching new data")
            except Exception as e:
                self.logger.error(f"Error loading cache: {e}")
        # Either no valid cache or empty data; fetch new data
        return self._fetch_data()

    def _fetch_data(self):
        """
        Fetch initiative data from official sources using the injected scraping logic.

        Returns:
            dict: Dictionary containing initiative data.
        """
        self.logger.info("Fetching initiatives data from official sources")
        try:
            base_url = "https://www.bk.admin.ch/ch/d/pore/vi/"
            url = f"{base_url}vis_2_2_5_1.html"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            initiatives = []
            rows = soup.find_all('tr')

            for row in rows:
                link_tag = row.find('a')
                if link_tag:
                    name = link_tag.text.strip()
                    href = link_tag.get('href')
                    initiative_link = base_url + href if href else None

                    # Use the <br> tag to try to get a review date, if available
                    review_tag = row.find('br')
                    review_date = review_tag.next_sibling.strip() if review_tag and review_tag.next_sibling else "Not Found"

                    # Build the initiative data dictionary.
                    initiative_data = {
                        'title': name,
                        'initiative_link': initiative_link,
                        'preliminary_review': review_date,
                    }

                    if initiative_link:
                        extra_data = self._scrape_initiative_page(initiative_link, base_url)
                        initiative_data.update(extra_data)

                    initiatives.append(initiative_data)

            if not initiatives:
                self.logger.warning("No initiatives found from scraping, using fallback data")
                return self._get_fallback_data()

            self._save_to_cache(initiatives)
            return {'initiatives': initiatives}

        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return self._get_fallback_data()

    def _scrape_initiative_page(self, initiative_url, base_url):
        """
        Scrape additional details from an initiative's page.

        Args:
            initiative_url (str): URL of the initiative page.
            base_url (str): Base URL to construct absolute links.

        Returns:
            dict: Dictionary with additional initiative details.
        """
        try:
            response = requests.get(initiative_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # === 1. Get the "initiative in full" link
            full_text_link = None
            full_text_content = None
            for a_tag in soup.find_all('a', href=True):
                text = a_tag.get_text(strip=True)
                if "Die Initiative im Wortlaut" in text:
                    full_text_link = base_url + a_tag['href']
                    break

            # === 2. Scrape full text content if link is found
            if full_text_link:
                try:
                    full_response = requests.get(full_text_link, timeout=30)
                    full_response.raise_for_status()
                    full_soup = BeautifulSoup(full_response.content, 'html.parser')
                    article_tag = full_soup.find('article')
                    if article_tag:
                        seen_paragraphs = set()
                        paragraphs = []
                        # Only look at direct children paragraphs to avoid duplicates
                        for p in article_tag.find_all('p', recursive=False):
                            text = p.get_text(separator=" ", strip=True)
                            normalized_text = " ".join(text.split()).lower()
                            if text and normalized_text not in seen_paragraphs and len(text) > 20:
                                seen_paragraphs.add(normalized_text)
                                paragraphs.append(text)
                        full_text_content = "\n".join(paragraphs)
                except Exception as e:
                    self.logger.warning(f"Could not fetch full text from {full_text_link}: {e}")

            # === 3. Initialize table data
            table_data = {
                'preliminary_examination_from': None,
                'expiry_of_collection_period': None,
                'start_of_collection': None,
                'voted_on': None,
                'submitted_on': None,
                'entry_into_force': None,
                'parliament_decision': None
            }

            # === 4. Parse all tables for metadata
            for table in soup.find_all('table'):
                for row in table.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        if "vorprüfung" in label:
                            table_data['preliminary_examination_from'] = value
                        elif "ablauf der sammelfrist" in label:
                            table_data['expiry_of_collection_period'] = value
                        elif "beginn der sammlung" in label:
                            table_data['start_of_collection'] = value
                        elif "eingereicht am" in label:
                            table_data['submitted_on'] = value
                        elif "zur abstimmung" in label:
                            table_data['voted_on'] = value
                        elif "inkrafttreten" in label:
                            table_data['entry_into_force'] = value
                        elif "beschluss des parlaments" in label or "parlamentsbeschluss" in label:
                            table_data['parliament_decision'] = value

            # === 5. Return collected data
            return {
                'full_text_link': full_text_link,
                'full_text': full_text_content,
                **table_data
            }

        except Exception as e:
            self.logger.error(f"Error scraping initiative page: {e}")
            return {}

    def _save_to_cache(self, initiatives):
        """
        Save fetched data to cache.

        Args:
            initiatives (list): List of initiative data.
        """
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': {'initiatives': initiatives}
            }
            with open(self.cache_file, 'w', encoding='utf-8') as file:
                json.dump(cache_data, file, ensure_ascii=False, indent=2)
            self.logger.info("Data saved to cache successfully")
        except Exception as e:
            self.logger.error(f"Error saving to cache: {e}")

    def _get_fallback_data(self):
        """
        Provide fallback data when fetching fails.

        Returns:
            dict: Dictionary containing minimal initiative data.
        """
        self.logger.warning("Using fallback data")
        return {
            'initiatives': [
                {'title': 'For responsible business', 'submission_date': '2016-10-10', 'status': 'Voted',
                 'result': 'Rejected'},
                {'title': 'For a ban on financing war material manufacturers', 'submission_date': '2018-06-21',
                 'status': 'Voted', 'result': 'Rejected'}
            ]
        }

    def get_all_initiatives(self):
        """
        Get all initiative data.
        """
        return self.initiatives_data.get('initiatives', [])

    def get_initiative_by_title(self, title):
        """
        Get initiative data by title.
        """
        initiatives = self.get_all_initiatives()
        for initiative in initiatives:
            if title.lower() in initiative.get('title', '').lower():
                return initiative
        return None

    def get_initiatives_by_status(self, status):
        """
        Get initiatives by status.
        """
        return [i for i in self.get_all_initiatives() if status.lower() in i.get('status', '').lower()]

    def get_initiatives_by_year(self, year):
        """
        Get initiatives by submission year.
        """
        return [i for i in self.get_all_initiatives() if year in i.get('submission_date', '')]

    def get_statistics(self):
        """
        Get statistics about initiatives.
        """
        initiatives = self.get_all_initiatives()
        status_counts = {}
        result_counts = {}
        year_counts = {}
        for initiative in initiatives:
            status = initiative.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            result = initiative.get('result', 'Unknown')
            result_counts[result] = result_counts.get(result, 0) + 1
            date = initiative.get('submission_date', '')
            year = date.split('-')[0] if '-' in date else date[:4]
            if year.isdigit():
                year_counts[year] = year_counts.get(year, 0) + 1
        return {
            'total': len(initiatives),
            'by_status': status_counts,
            'by_result': result_counts,
            'by_year': year_counts
        }