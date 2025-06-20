import streamlit as st
import requests
import json

st.title("🧬 Research AI - Direct Connection")

def search_papers(query, limit=3):
    """Search papers using direct Supabase API"""
