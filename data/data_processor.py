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
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')

        # Initialize data
        self._prepare_data()

    def _prepare_data(self):
        """
        Prepare the data for processing and searching.
        """
        # Get the initiatives data from DataFetcher
        initiatives = self.data_fetcher.get_all_initiatives()
        if not initiatives:
            raise ValueError("No initiatives data found.")

        # Convert to DataFrame
        self.initiatives_df = pd.DataFrame(initiatives)

        # Debug: Show sample data
        print(f"Loaded {len(self.initiatives_df)} initiatives.")
        print("Sample row:", self.initiatives_df.iloc[0].to_dict())

        # Build a text corpus by combining multiple fields available from the data
        self.initiatives_df['text_corpus'] = self.initiatives_df.apply(
            lambda row: ' '.join(filter(None, [
                str(row.get('title', '')).strip(),
                str(row.get('status', '')).strip(),
                str(row.get('result', '')).strip(),
                str(row.get('preliminary_review', '')).strip(),
                str(row.get('submitted_on', '')).strip(),
                str(row.get('full_text', '')).strip()  # Add full_text to the corpus
            ])),
            axis=1
        )

        # Clean up the texts
        texts = self.initiatives_df['text_corpus'].fillna('').astype(str)
        texts = texts[texts.str.strip() != '']

        # Fallback: Use only titles if the combined text is empty
        if texts.empty:
            print("⚠️ Empty TF-IDF input. Falling back to using titles only.")
            self.initiatives_df['text_corpus'] = self.initiatives_df['title'].fillna('').astype(str)
            texts = self.initiatives_df['text_corpus'].fillna('').astype(str)
            texts = texts[texts.str.strip() != '']

            if texts.empty:
                raise ValueError("No valid text data even from titles. Cannot proceed.")

        # Initialize TF-IDF vectorizer with custom preprocessing
        self.vectorizer = TfidfVectorizer(
            tokenizer=self._preprocess_text,
            stop_words=stopwords.words('english') +
                       stopwords.words('german') +
                       stopwords.words('french') +
                       stopwords.words('italian')
        )

        # Fit the vectorizer to the text corpus
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def _preprocess_text(self, text):
        """
        Preprocess text for better search results.

        Args:
            text (str): Text to preprocess

        Returns:
            list: List of preprocessed tokens
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
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
        query_vector = self.vectorizer.transform([query])
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        top_indices = similarity_scores.argsort()[-top_n:][::-1]

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

    def get_initiatives_by_category(self, category):
        """
        Get initiatives by category.

        Args:
            category (str): Category to filter by (e.g., 'Restaurant', 'Hotel')

        Returns:
            list: Initiatives filtered by category
        """
        return [i for i in self.data_fetcher.get_all_initiatives() if category.lower() in i.get('category', '').lower()]