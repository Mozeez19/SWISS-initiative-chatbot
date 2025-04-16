import re
import random
import difflib  # Standard library for fuzzy matching
from data.data_processor import DataProcessor
from summarize_initiative import summarize_initiative

class Chatbot:
    """
    Chatbot class for handling user queries about Swiss initiatives.
    """

    def __init__(self, data_fetcher):
        """
        Initialize the Chatbot.

        Args:
            data_fetcher (DataFetcher): Instance of DataFetcher class
        """
        self.data_processor = DataProcessor(data_fetcher)
        self.data_fetcher = data_fetcher
        self.greeting_responses = [
            "Hello! I'm your Swiss Initiatives Chatbot. How can I help you today?",
            "Grüezi! Ask me anything about Swiss popular initiatives.",
            "Bonjour! I'm here to answer your questions about Swiss initiatives.",
            "Buongiorno! What would you like to know about Swiss popular initiatives?"
        ]
        self.farewell_responses = [
            "Goodbye! Feel free to return if you have more questions.",
            "Auf Wiedersehen! Come back anytime.",
            "Au revoir! Happy to help you again soon.",
            "Arrivederci! Have a great day!"
        ]
        self.fallback_responses = [
            "I'm not sure I understand. Could you rephrase your question about Swiss initiatives?",
            "I don't have information about that. Would you like to know about specific Swiss initiatives?",
            "I can help with questions about Swiss popular initiatives. What would you like to know?"
        ]

    def get_response(self, user_input):
        """
        Generate a response to user input.
        """
        user_input = user_input.lower()

        if self._is_greeting(user_input):
            return random.choice(self.greeting_responses)

        if self._is_farewell(user_input):
            return random.choice(self.farewell_responses)

        initiative_match = self._check_initiative_specific_question(user_input)
        if initiative_match:
            return initiative_match

        process_info = self._check_process_question(user_input)
        if process_info:
            return process_info

        stats_info = self._check_statistics_question(user_input)
        if stats_info:
            return stats_info

        search_results = self.data_processor.search_initiatives(user_input)
        if search_results:
            response = "Here's what I found related to your query:\n\n"
            for i, result in enumerate(search_results, 1):
                summary = summarize_initiative(result)
                response += f"{i}. **{result.get('title', 'Untitled Initiative')}**\n"
                response += f"   Status: {result.get('status', 'Unknown')}\n"
                if 'description' in result and result['description']:
                    response += f"   {result.get('description')}\n"
                response += f"   **Summary**: {summary}\n\n"
            response += "Would you like more details about any of these initiatives?"
            return response

        return random.choice(self.fallback_responses)

    def _is_greeting(self, text):
        greetings = ['hello', 'hi', 'hey', 'grüezi', 'bonjour', 'buongiorno', 'greetings']
        return any(greeting in text for greeting in greetings)

    def _is_farewell(self, text):
        farewells = ['bye', 'goodbye', 'auf wiedersehen', 'au revoir', 'arrivederci', 'ciao', 'see you']
        return any(farewell in text for farewell in farewells)

    def _check_initiative_specific_question(self, text):
        """
        Checks if the query is about a specific initiative. Uses regex patterns to extract
        a candidate name and then, using fuzzy matching, returns the best match.
        """
        patterns = [
            r'(tell|talk|know|information).+about\s+(.+)',
            r'what (is|was|are|were)\s+(.+)',
            r'details\s+(?:on|about)\s+(.+)'
        ]

        candidate = None
        # Try to extract candidate initiative name from the query
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(2) if match.lastindex >= 2 and match.group(2) else match.group(1)
                break

        if not candidate:
            return None

        # Use the search function to get a list of candidate initiatives
        results = self.data_processor.search_initiatives(candidate, top_n=5)
        if not results:
            return None

        # Use difflib to compute similarity ratios and pick the best match.
        best_match = None
        best_score = 0.0
        for initiative in results:
            title = initiative.get("title", "")
            score = difflib.SequenceMatcher(None, candidate.lower(), title.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = initiative

        # If best match found above threshold (say, 0.5), return its detailed information.
        if best_match and best_score > 0.5:
            summary = summarize_initiative(best_match)
            return self._format_initiative_details(best_match, summary)
        else:
            return None

    def _format_initiative_details(self, initiative, summary):
        response = f"**{initiative.get('title', 'Untitled Initiative')}**\n\n"

        if 'submission_date' in initiative:
            response += f"**Submission Date**: {initiative['submission_date']}\n"
        if 'status' in initiative:
            response += f"**Status**: {initiative['status']}\n"
        if 'result' in initiative:
            response += f"**Result**: {initiative['result']}\n"
        if 'description' in initiative and initiative['description']:
            response += f"\n**Description**:\n{initiative['description']}\n"

        response += f"\n**Summary**: {summary}\n"
        return response

    def _check_process_question(self, text):
        process_keywords = ['how does an initiative work', 'what is a popular initiative', 'process', 'requirements',
                            'how many signatures', 'timeline']
        if any(re.search(keyword, text, re.IGNORECASE) for keyword in process_keywords):
            return (
                "**Swiss Popular Initiative Process**\n\n"
                "1. **Formation of a committee**: 7-27 Swiss citizens form a committee.\n"
                "2. **Submission of text**: Initiative text is submitted for validation.\n"
                "3. **Collection of signatures**: 100,000 valid signatures within 18 months.\n"
                "4. **Validation**: The government verifies the signatures.\n"
                "5. **Parliament Review**: Parliament debates the initiative.\n"
                "6. **Popular Vote**: Requires majority votes from people & cantons.\n"
            )
        return None

    def _check_statistics_question(self, text):
        stats_keywords = ['statistics', 'how many initiatives', 'success rate', 'percentage', 'numbers', 'data', 'figures']
        if any(keyword in text for keyword in stats_keywords):
            stats = self.data_fetcher.get_statistics()
            response = f"**Total initiatives**: {stats.get('total', 0)}\n\n"
            if 'by_status' in stats:
                response += "**By status**:\n" + "\n".join(
                    [f"- {k}: {v}" for k, v in stats['by_status'].items()]
                ) + "\n\n"
            if 'by_result' in stats:
                response += "**By result**:\n" + "\n".join(
                    [f"- {k}: {v}" for k, v in stats['by_result'].items()]
                ) + "\n\n"
            return response
        return None
