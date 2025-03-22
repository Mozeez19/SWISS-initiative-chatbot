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
        cache_duration(int): Duration in seconds for which to cache data.
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

                if (current_time - cache_time).total_seconds() < self.cache_duration:
                    self.logger.info("Loading initiatives data from cache")
                    return cache_data.get('data', {})
            except Exception as e:
                self.logger.error(f"Error loading cache: {e}")

        return self._fetch_data()

    def _fetch_data(self):
        """
        Fetch initiative data from official sources.

        Returns:
        dict: Dictionary containing initiative data.
        """
        self.logger.info("Fetching initiatives data from official sources")
        try:
            url = "https://www.bk.admin.ch/ch/d/pore/vi/vis_2_2_5_1.html"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            initiatives = []
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        initiative = {
                            'title': cols[0].text.strip(),
                            'submission_date': cols[1].text.strip(),
                            'status': cols[2].text.strip(),
                            'result': cols[3].text.strip()
                        }
                        initiatives.append(initiative)

            self._save_to_cache(initiatives)
            return {'initiatives': initiatives}
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return self._get_fallback_data()

    def _save_to_cache(self, data):
        """
        Save fetched data to cache.

        Args:
        data(list): List of initiative data.
        """
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': {'initiatives': data}
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
            if title.lower() in initiative['title'].lower():
                return initiative
        return None

    def get_initiatives_by_status(self, status):
        """
        Get initiatives by status.
        """
        return [i for i in self.get_all_initiatives() if status.lower() in i['status'].lower()]

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
