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
from datetime import datetime
import os
from openai import OpenAI

from src import chatbot


# Initialize OpenAI client (uses environment variable for API key)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_openai(messages):
    """
    Call the OpenAI API with the conversation history.

    Args:
        messages (list): List of dicts like {"role": "user", "content": "..."}
    Returns:
        str: The assistant’s reply generated by OpenAI.
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return completion.choices[0].message.content.strip()


class UI:
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.data_processor = chatbot.data_processor
        self.data_fetcher = chatbot.data_fetcher

    def render(self):
        tab1, tab2, tab3 = st.tabs(["Chatbot", "Initiatives Database", "Statistics"])

        with tab1:
            self._render_chat_messages()

        with tab2:
            self._render_database()

        with tab3:
            self._render_statistics()

        self._render_chat_input()  # Render input at the bottom, outside tab1

    def _render_chat_messages(self):
        st.header("Chat with the Swiss Initiatives Bot")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Hello! I'm your Swiss Initiatives Chatbot. Ask me anything about Swiss initiatives, public reactions, or direct democracy.",
                    }
                ]
                st.rerun()

        with col2:
            st.checkbox(
                "Use OpenAI Generative Model",
                key="use_openai",
                value=st.session_state.get("use_openai", False),
                help="Tick this box to generate responses using OpenAI's GPT models instead of the built-in chatbot logic.",
            )

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Hello! I'm your Swiss Initiatives Chatbot. Ask me anything about Swiss initiatives, public reactions, or direct democracy.",
                }
            ]

        for message in st.session_state.messages[-20:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def _render_chat_input(self):
        prompt = st.chat_input("Ask a question about Swiss initiatives...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    if st.session_state.get("use_openai", False):
                        response = ask_openai(st.session_state.messages)
                    else:
                        result = self.chatbot.get_response(prompt)
                        if isinstance(result, tuple):
                            initiative, response = result
                        else:
                            response = result
                except Exception as e:
                    response = f"⚠️ Error calling chatbot: {e}"
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    def _render_database(self):
        st.header("Swiss Initiatives Database")

        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox("Filter by:", ["All", "Status", "Year", "Search by keyword"])

        all_initiatives = self.data_fetcher.get_all_initiatives()
        filtered_initiatives = all_initiatives

        if filter_type == "Status":
            with col2:
                statuses = set(i.get("status", "") for i in all_initiatives)
                selected_status = st.selectbox("Select status:", sorted(statuses))
                filtered_initiatives = self.data_fetcher.get_initiatives_by_status(selected_status)

        elif filter_type == "Year":
            with col2:
                years = set()
                for i in all_initiatives:
                    date = i.get("submitted_on", "") or i.get("submission_date", "")
                    year = date.split("-")[0] if "-" in date else date[:4]
                    if year.isdigit():
                        years.add(year)
                selected_year = st.selectbox("Select year:", sorted(years, reverse=True))
                filtered_initiatives = [i for i in all_initiatives if
                                        selected_year in (i.get("submitted_on", "") or "")]

        elif filter_type == "Search by keyword":
            with col2:
                keyword = st.text_input("Enter keyword:")
                if keyword:
                    filtered_initiatives = self.data_processor.search_initiatives(keyword, top_n=50)

        def get_date(initiative):
            date_str = initiative.get("submitted_on", "") or initiative.get("submission_date", "")
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return datetime.min

        filtered_initiatives = sorted(filtered_initiatives, key=get_date, reverse=True)

        st.markdown(f"### Showing {len(filtered_initiatives)} Initiative(s)")
        for initiative in filtered_initiatives:
            with st.expander(initiative.get("title", "Untitled")):
                st.markdown(f"**Status:** {initiative.get('status', 'N/A')}")
                st.markdown(f"**Result:** {initiative.get('result', 'N/A')}")
                st.markdown(f"**Submitted on:** {initiative.get('submitted_on', 'N/A')}")
                st.markdown(f"**Summary:** {initiative.get('summary', 'No summary available.')}")
                st.markdown(f"**Positions in Favor:** {initiative.get('positions_for', 'None')}")
                st.markdown(f"**Positions Against:** {initiative.get('positions_against', 'None')}")
                if initiative.get("full_text_link"):
                    st.markdown(f"[Read full text of the initiative]({initiative['full_text_link']})",
                                unsafe_allow_html=True)

    def _render_statistics(self):
        st.header("Statistics of Swiss Initiatives")
        all_initiatives = self.data_fetcher.get_all_initiatives()
        if not all_initiatives:
            st.warning("No data available.")
            return

        df = pd.DataFrame(all_initiatives)

        if 'submitted_on' in df.columns:
            df['submitted_on'] = pd.to_datetime(df['submitted_on'], errors='coerce')
            df['year'] = df['submitted_on'].dt.year
            initiatives_per_year = df['year'].value_counts().sort_index()
            fig = px.bar(
                initiatives_per_year,
                x=initiatives_per_year.index,
                y=initiatives_per_year.values,
                labels={'x': 'Year', 'y': 'Number of Initiatives'},
                title='Number of Initiatives per Year'
            )
            st.plotly_chart(fig)
        else:
            st.warning("'submitted_on' field missing.")

        if 'status' in df.columns:
            status_counts = df['status'].value_counts()
            fig = px.pie(
                names=status_counts.index,
                values=status_counts.values,
                title='Distribution of Initiative Statuses'
            )
            st.plotly_chart(fig)





# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
#
# """
# UI Module
#
# This module implements the user interface for the Swiss initiative chatbot
# using Streamlit.
# """
#
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from datetime import datetime
# import requests  # NEW: import requests for Mistral API calls
#
# from src import chatbot
#
#
# def ask_mistral(messages):
#     """
#     Call the Ollama endpoint for Mistral with the conversation history.
#
#     Args:
#         messages (list): List of message dicts representing the conversation.
#     Returns:
#         str: The assistant’s reply generated by Mistral.
#     """
#     url = "http://localhost:11434/api/chat"
#     payload = {
#         "model": "mistral",
#         "messages": messages,
#         "stream": False
#     }
#     response = requests.post(url, json=payload)
#     response.raise_for_status()
#     return response.json()["message"]["content"]
#
#
# class UI:
#     def __init__(self, chatbot):
#         self.chatbot = chatbot
#         self.data_processor = chatbot.data_processor
#         self.data_fetcher = chatbot.data_fetcher
#
#     def render(self):
#         tab1, tab2, tab3 = st.tabs(["Chatbot", "Initiatives Database", "Statistics"])
#         with tab1:
#             self._render_chatbot()
#         with tab2:
#             self._render_database()
#         with tab3:
#             self._render_statistics()
#
#     def _render_chatbot(self):
#         st.header("Chat with the Swiss Initiatives Bot")
#
#         # NEW: Checkbox to select using Mistral via Ollama for response generation.
#         use_mistral = st.checkbox(
#             "Use Mistral Generative Model",
#             value=False,
#             help="Tick this box to generate responses using Mistral via Ollama instead of the built-in chatbot logic."
#         )
#
#         if "messages" not in st.session_state:
#             st.session_state.messages = [
#                 {
#                     "role": "assistant",
#                     "content": "Hello! I'm your Swiss Initiatives Chatbot. Ask me anything about Swiss initiatives, public reactions, or direct democracy.",
#                 }
#             ]
#
#         # Display chat history.
#         for message in st.session_state.messages:
#             with st.chat_message(message["role"]):
#                 st.markdown(message["content"])
#
#         # Get new prompt.
#         if prompt := st.chat_input("Ask a question about Swiss initiatives..."):
#             st.session_state.messages.append({"role": "user", "content": prompt})
#             with st.chat_message("user"):
#                 st.markdown(prompt)
#
#             # Choose response source based on checkbox.
#             if use_mistral:
#                 try:
#                     response = ask_mistral(st.session_state.messages)
#                 except Exception as e:
#                     response = f"Error calling Mistral: {e}"
#             else:
#                 response = self.chatbot.get_response(prompt)
#
#             st.session_state.messages.append({"role": "assistant", "content": response})
#             with st.chat_message("assistant"):
#                 st.markdown(response)
#
#     def _render_database(self):
#         st.header("Swiss Initiatives Database")
#
#         col1, col2 = st.columns(2)
#         with col1:
#             filter_type = st.selectbox("Filter by:", ["All", "Status", "Year", "Search by keyword"])
#
#         all_initiatives = self.data_fetcher.get_all_initiatives()
#         filtered_initiatives = all_initiatives
#
#         if filter_type == "Status":
#             with col2:
#                 statuses = set(i.get("status", "") for i in all_initiatives)
#                 selected_status = st.selectbox("Select status:", sorted(statuses))
#                 filtered_initiatives = self.data_fetcher.get_initiatives_by_status(selected_status)
#
#         elif filter_type == "Year":
#             with col2:
#                 years = set()
#                 for i in all_initiatives:
#                     date = i.get("submitted_on", "") or i.get("submission_date", "")
#                     year = date.split("-")[0] if "-" in date else date[:4]
#                     if year.isdigit():
#                         years.add(year)
#                 selected_year = st.selectbox("Select year:", sorted(years, reverse=True))
#                 filtered_initiatives = [i for i in all_initiatives if
#                                         selected_year in (i.get("submitted_on", "") or "")]
#
#         elif filter_type == "Search by keyword":
#             with col2:
#                 keyword = st.text_input("Enter keyword:")
#                 if keyword:
#                     filtered_initiatives = self.data_processor.search_initiatives(keyword, top_n=50)
#
#         # Sort by submission date descending
#         def get_date(initiative):
#             date_str = initiative.get("submitted_on", "") or initiative.get("submission_date", "")
#             try:
#                 return datetime.strptime(date_str, "%Y-%m-%d")
#             except:
#                 return datetime.min
#
#         filtered_initiatives = sorted(filtered_initiatives, key=get_date, reverse=True)
#
#         st.markdown(f"### Showing {len(filtered_initiatives)} Initiative(s)")
#         for initiative in filtered_initiatives:
#             with st.expander(initiative.get("title", "Untitled")):
#                 st.markdown(f"**Status:** {initiative.get('status', 'N/A')}")
#                 st.markdown(f"**Result:** {initiative.get('result', 'N/A')}")
#                 st.markdown(f"**Submitted on:** {initiative.get('submitted_on', 'N/A')}")
#                 st.markdown(f"**Summary:** {initiative.get('summary', 'No summary available.')}")
#                 st.markdown(f"**Positions in Favor:** {initiative.get('positions_for', 'None')}")
#                 st.markdown(f"**Positions Against:** {initiative.get('positions_against', 'None')}")
#                 if initiative.get("full_text_link"):
#                     st.markdown(f"[Read full text of the initiative]({initiative['full_text_link']})",
#                                 unsafe_allow_html=True)
#
#     def _render_statistics(self):
#         st.header("Statistics of Swiss Initiatives")
#         all_initiatives = self.data_fetcher.get_all_initiatives()
#         if not all_initiatives:
#             st.warning("No data available.")
#             return
#
#         df = pd.DataFrame(all_initiatives)
#
#         if 'submitted_on' in df.columns:
#             df['submitted_on'] = pd.to_datetime(df['submitted_on'], errors='coerce')
#             df['year'] = df['submitted_on'].dt.year
#             initiatives_per_year = df['year'].value_counts().sort_index()
#             fig = px.bar(
#                 initiatives_per_year,
#                 x=initiatives_per_year.index,
#                 y=initiatives_per_year.values,
#                 labels={'x': 'Year', 'y': 'Number of Initiatives'},
#                 title='Number of Initiatives per Year'
#             )
#             st.plotly_chart(fig)
#         else:
#             st.warning("'submitted_on' field missing.")
#
#         if 'status' in df.columns:
#             status_counts = df['status'].value_counts()
#             fig = px.pie(
#                 names=status_counts.index,
#                 values=status_counts.values,
#                 title='Distribution of Initiative Statuses'
#             )
#             st.plotly_chart(fig)
