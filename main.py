# main.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
from src.ui import UI
from src.chatbot import Chatbot
from data.data_fetcher import DataFetcher


def main():
    """
    Main function to initialize and run the application.
    """

    # Set page configuration
    st.set_page_config(
        page_title="Swiss Initiative Chatbot",
        page_icon="🇨🇭",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Application title
    st.title("Swiss Popular Initiative Chatbot")
    st.markdown("Ask questions about Swiss popular initiatives and referendums")

    # Initialize data fetcher
    data_fetcher = DataFetcher()

    # Initialize chatbot with the fetched data
    chatbot = Chatbot(data_fetcher)

    # Initialize and render UI
    ui = UI(chatbot)
    ui.render()


if __name__ == "__main__":
    main()