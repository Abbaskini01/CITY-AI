import streamlit as st
import pandas as pd
import json

# --- Page Configuration (from UI/UX Doc) ---
st.set_page_config(
    page_title="CityAI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Main Application ---
st.title("CityAI – The GenAI Smart City Assistant 🤖")
st.caption("Transforming Urban Life, One AI Conversation at aTime")

st.write("Welcome to CityAI! Our systems are initializing.")
st.write("Phase 1 is complete. We are ready for Phase 2.")

# Placeholder for data loading
try:
    with open('data/facilities.json', 'r') as f:
        facilities = json.load(f)
    st.subheader("✅ Data Loaded Successfully:")
    st.json(facilities[0], expanded=False) # Show first facility as a test
except FileNotFoundError:
    st.error("Error: The 'data/facilities.json' file was not found.")
except Exception as e:
    st.error(f"An error occurred while loading data: {e}")

# --- Sidebar ---
with st.sidebar:
    st.header("CityAI")
    st.write("Your guide to a smarter city.")
    st.subheader("Daily Tip")
    st.info("We will load a random tip from `tips.json` here in Phase 2.")