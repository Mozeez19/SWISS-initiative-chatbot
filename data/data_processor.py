import util
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DataProcessor:
    """
    Class to process and prepare Swiss initiative data for the chatbot.
    """

    def __init__(self, data_fetcher):
        """
        Initialize the DataProcessor.

        Args:
            data_fetcher (DataFetcher): Instance of DataFetcher class
        """
        self.data_fetcher = data_fetcher
        self.initiatives_df = None
        self.vectorizer = None
        self.tfidf_matrix = None

        # Download NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('punkt_tab')

        # Initialize data
        self._prepare_data()

    def _prepare_data(self):
        """
        Prepare the data for processing and searching.
        """
        # Get the initiatives data
        initiatives = self.data_fetcher.get_all_initiatives()

        # Convert to DataFrame for easier processing
        self.initiatives_df = pd.DataFrame(initiatives)

        # Create a text corpus for searching
        self.initiatives_df['text_corpus'] = self.initiatives_df.apply(
            lambda row: ' '.join([
                str(row.get('title', '')),
                str(row.get('description', '')),
                str(row.get('status', '')),
                str(row.get('result', ''))
            ]),
            axis=1
        )

        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            tokenizer=self._preprocess_text,
            stop_words=stopwords.words('english') +
                       stopwords.words('german') +
                       stopwords.words('french') +
                       stopwords.words('italian')
        )

        # Create TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(self.initiatives_df['text_corpus'].fillna(''))

    def _preprocess_text(self, text):
        """
        Preprocess text for better search results.

        Args:
            text (str): Text to preprocess

        Returns:
            list: List of preprocessed tokens
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)

        # Tokenize
        tokens = word_tokenize(text)

        return tokens

    def search_initiatives(self, query, top_n=5):
        """
        Search initiatives based on a query.

        Args:
            query (str): Search query
            top_n (int): Number of top results to return

        Returns:
            list: List of matching initiatives
        """
        # Preprocess and vectorize query
        query_vector = self.vectorizer.transform([query])

        # Compute similarity
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # Get top N matching initiatives
        top_indices = similarity_scores.argsort()[-top_n:][::-1]

        # Filter out low similarity scores
        results = [
            self.initiatives_df.iloc[idx].to_dict()
            for idx in top_indices
            if similarity_scores[idx] > 0.1  # Threshold for relevance
        ]

        return results

    def get_initiative_details(self, initiative_title):
        """
        Get detailed information about a specific initiative.

        Args:
            initiative_title (str): Title of the initiative

        Returns:
            dict: Initiative details
        """
        return self.data_fetcher.get_initiative_by_title(initiative_title)

    def get_statistics_data(self):
        """
        Get processed statistics data for visualization.

        Returns:
            dict: Processed statistics
        """
        stats = self.data_fetcher.get_statistics()

        # Process data for visualization
        status_data = pd.Series(stats.get('by_status', {})).reset_index()
        status_data.columns = ['Status', 'Count']

        result_data = pd.Series(stats.get('by_result', {})).reset_index()
        result_data.columns = ['Result', 'Count']

        year_data = pd.Series(stats.get('by_year', {})).reset_index()
        year_data.columns = ['Year', 'Count']
        year_data = year_data.sort_values('Year')

        return {
            'total': stats.get('total', 0),
            'status_data': status_data.to_dict('records'),
            'result_data': result_data.to_dict('records'),
            'year_data': year_data.to_dict('records')
        }
