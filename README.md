# 🇨🇭 Swiss Popular Initiative Chatbot :robot:

A chatbot application that provides detailed information about Swiss popular initiatives. The application fetches data from official government sources, processes it intelligently, and offers a user-friendly interface where users can ask questions about specific initiatives and get relevant insights.

---

## 🧠 Features

- [x] Retrieves metadata and full texts from Swiss federal initiative pages
- [x] Uses NLP and LLMs to summarize initiatives and extract keywords
- [x] Answers user questions via a smart chatbot interface
- [ ] Displays public sentiment using scraped data from online sources
- [x] Interactive UI built with Streamlit
- [x] Search and similarity matching with fuzzy logic

![mechanism ](https://github.com/Mozeez19/SWISS-initiative-chatbot/blob/87aba30947990274709c263b6ef87bf09f462d8d/Web%20scrape.png)

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

## 🗂️ Project Structure
Important structure of the project
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


## 🧪 Usage

Once the app is running, open your browser to the Streamlit interface. You can ask questions like:

- "What is the initiative on pension reform?"  
- "When was the initiative on CO2 emissions submitted?"  
- "What was the outcome of the initiative on food security?"

The chatbot will return:

- A summary of the initiative  
- Key dates and metadata   
- Direct links to official documentation  


---

## 📄 License



---

## ❤️ Acknowledgements

- **Swiss Confederation** for public access to initiative data  
- **HuggingFace** for transformer models  
- **OpenAI / Mistral** for LLM APIs  
- **Streamlit** for rapid UI prototyping

## 📸 Screenshots

Here are a few snapshots of the app in action:

### 🏠 Home Page
![Home Screen](https://github.com/Mozeez19/SWISS-initiative-chatbot/blob/e99ff65205f90fdccccaf6e8a74aac1ad40e7c94/Screenshot%20(206)1.png)

![](https://github.com/Mozeez19/SWISS-initiative-chatbot/blob/1b5e71dd567ce9b251ad2453e8f5cbc1db0e397b/Screenshot%20(207)2.png)

![](https://github.com/Mozeez19/SWISS-initiative-chatbot/blob/1b5e71dd567ce9b251ad2453e8f5cbc1db0e397b/Screenshot%20(209)3.png)

### 🤖 Chatbot in Action
![Chatbot Demo](https://github.com/Mozeez19/SWISS-initiative-chatbot/blob/d37fe29cb2610663096a563c2b054743a22759f7/Screenshot%20(210)%20chatInAct.png)

### 💾 Database Tab
![Database Tab](https://github.com/Mozeez19/SWISS-initiative-chatbot/blob/0f7c0bc38036d81a0dfcfea969dd2fcd2ae13033/Screenshot%20(199)Db.png)

### 📊 Statistics Tab
![chart Tab](https://github.com/Mozeez19/SWISS-initiative-chatbot/blob/183626878f2401a03da6495229032615b09f2243/Screenshot%20(200)chart.png)



## 📄 To do 
 - [ ] Add Relevant sentiment and reactions
 - [ ] Update UI
 - [ ] Fix the database Tab
