# src/ui.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI Module

This module implements the user interface for the Swiss initiative chatbot
using Streamlit.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src import chatbot


class UI:
    """
    User interface class for the Swiss initiative chatbot.
    """

    def __init__(self, chatbot):
        """
        Initialize the UI.

        Args:
            chatbot (Chatbot): Instance of the Chatbot class.
        """
        self.chatbot = chatbot
        self.data_processor = self.chatbot.data_processor
        self.data_fetcher = self.chatbot.data_fetcher

    def render(self):
        """
        Render the UI.
        """
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["Chatbot", "Initiatives Database", "Statistics"])

        with tab1:
            self._render_chatbot()

        with tab2:
            self._render_database()

        with tab3:
            self._render_statistics()

    def _render_chatbot(self):
        """
        Render the chatbot interface.
        """
        st.header("Chat with the Swiss Initiatives Bot")

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Hello! I'm your Swiss Initiatives Chatbot. Ask me anything about Swiss popular initiatives, referendums, or the direct democracy system in Switzerland.",
                }
            ]

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about Swiss initiatives..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get chatbot response
            response = self.chatbot.get_response(prompt)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)

    def _render_database(self):
        """
        Render the initiatives database interface.
        """
        st.header("Swiss Initiatives Database")

        # Create filters
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_type = st.selectbox(
                "Filter by:", ["All", "Status", "Year", "Search by keyword"]
            )

        # Get all initiatives
        all_initiatives = self.data_fetcher.get_all_initiatives()
        filtered_initiatives = all_initiatives

        # Apply filters
        if filter_type == "Status":
            with col2:
                # Extract unique statuses
                statuses = set(i.get("status", "") for i in all_initiatives)
                selected_status = st.selectbox("Select status:", sorted(list(statuses)))

                # Filter by selected status
                filtered_initiatives = self.data_fetcher.get_initiatives_by_status(
                    selected_status
                )

        elif filter_type == "Year":
            with col2:
                # Extract unique years
                years = set()
                for i in all_initiatives:
                    date = i.get("submission_date", "")
                    year = date.split("-")[0] if "-" in date else date[:4]
                    if year.isdigit():
                        years.add(year)

                selected_year = st.selectbox(
                    "Select year:", sorted(list(years), reverse=True)
                )

    def _render_statistics(self):
        """
        Render statistics related to Swiss initiatives.
        """
        st.header("Statistics of Swiss Initiatives")

        # Fetch all initiatives
        all_initiatives = self.data_fetcher.get_all_initiatives()

        if not all_initiatives:
            st.warning("No data available to display statistics.")
            return

        # Convert initiatives data to a DataFrame
        df = pd.DataFrame(all_initiatives)

        # Ensure 'submission_date' is in datetime format
        if 'submission_date' in df.columns:
            df['submission_date'] = pd.to_datetime(df['submission_date'], errors='coerce')

            # Extract year from 'submission_date'
            df['year'] = df['submission_date'].dt.year

            # Count initiatives per year
            initiatives_per_year = df['year'].value_counts().sort_index()

            # Plot initiatives per year
            fig = px.bar(
                initiatives_per_year,
                x=initiatives_per_year.index,
                y=initiatives_per_year.values,
                labels={'x': 'Year', 'y': 'Number of Initiatives'},
                title='Number of Initiatives per Year'
            )
            st.plotly_chart(fig)
        else:
            st.warning("'submission_date' column is missing in the data.")

        # Display status distribution if 'status' column exists
        if 'status' in df.columns:
            status_counts = df['status'].value_counts()

            # Plot status distribution
            fig = px.pie(
                names=status_counts.index,
                values=status_counts.values,
                title='Distribution of Initiative Statuses'
            )
            st.plotly_chart(fig)
        else:
            st.warning("'status' column is missing in the data.")
