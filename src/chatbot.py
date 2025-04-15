# src/chatbot.py

import re
import random
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
        patterns = [
            r'(tell|talk|know|information).+about\s+(.+)',
            r'what (is|was|are|were)\s+(.+)',
            r'details\s+(?:on|about)\s+(.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                initiative_name = match.group(2) if len(match.groups()) > 1 else match.group(1)
                initiative = self.data_fetcher.get_initiative_by_title(initiative_name)
                if initiative:
                    summary = summarize_initiative(initiative)
                    return self._format_initiative_details(initiative, summary)
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
        if any(re.search(keyword, text) for keyword in process_keywords):
            return """
            **Swiss Popular Initiative Process**

            1. **Formation of a committee**: 7-27 Swiss citizens form a committee.
            2. **Submission of text**: Initiative text is submitted for validation.
            3. **Collection of signatures**: 100,000 valid signatures within 18 months.
            4. **Validation**: The government verifies the signatures.
            5. **Parliament Review**: Parliament debates the initiative.
            6. **Popular Vote**: Requires majority votes from people & cantons.
            """
        return None

    def _check_statistics_question(self, text):
        stats_keywords = ['statistics', 'how many initiatives', 'success rate', 'percentage', 'numbers', 'data',
                          'figures']
        if any(keyword in text for keyword in stats_keywords):
            stats = self.data_fetcher.get_statistics()
            response = f"**Total initiatives**: {stats.get('total', 0)}\n\n"
            if 'by_status' in stats:
                response += "**By status**:\n" + "\n".join(
                    [f"- {k}: {v}" for k, v in stats['by_status'].items()]) + "\n\n"
            if 'by_result' in stats:
                response += "**By result**:\n" + "\n".join(
                    [f"- {k}: {v}" for k, v in stats['by_result'].items()]) + "\n\n"
            return response
        return None
