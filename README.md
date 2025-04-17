# 🇨🇭 Swiss Popular Initiative Chatbot

A chatbot application that provides detailed information about Swiss popular initiatives. The application fetches data from official government sources, processes it intelligently, and offers a user-friendly interface where users can ask questions about specific initiatives and get relevant insights.

---

## 🧠 Features

- Retrieves metadata and full texts from Swiss federal initiative pages
- Uses NLP and LLMs to summarize initiatives and extract keywords
- Answers user questions via a smart chatbot interface
- Displays public sentiment using scraped data from online sources
- Interactive UI built with Streamlit
- Search and similarity matching with fuzzy logic

---

## 🧰 Technologies Used

- **Python 3.10**
- Streamlit
- BeautifulSoup
- Transformers (HuggingFace)
- OpenAI / Mistral (LLM)
- pandas
- requests
- matplotlib
- nltk
- scikit-learn
- plotly
- difflib

---

## 🚀 Installation

To get started with the chatbot locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/swiss-initiative-chatbot.git
   cd swiss-initiative-chatbot
   
 2. **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate        # On Windows: venv\Scripts\activate

 3. **Install the dependencies**
    ```bash
    pip install -r requirements.txt

 5. **Run the Streamlit app**
    ```bash
    streamlit run src/main.py

 7. tytyt
 8. tuyuy
 9. 
## 🗂️ Project Structure
 ```bash
 swiss-initiative-chatbot/
├── data/                        # Raw and processed data
├── src/
│   ├── chatbot.py               # Chatbot logic and response handling
│   ├── data_processor.py        # Initiative scraper and data parser
│   ├── summarizer.py            # Summarization and keyword extraction
│   ├── opinion_analyzer.py      # Sentiment and public reaction analyzer
│   └── ui.py                    # Streamlit-based user interface
├── summarized_initiatives.json # Cached summaries of initiatives
├── requirements.txt
└── README.md

