import streamlit as st
import pandas as pd
import json
import random  # We'll use this to pick a random tip

# --- Page Configuration (from UI/UX Doc) ---
st.set_page_config(
    page_title="CityAI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. Smart Data Loading (with Caching) ---
# This function loads data from our JSON files.
# @st.cache_data tells Streamlit to run this function only once
# and store the result, improving performance.

@st.cache_data
def load_data():
    try:
        with open('data/facilities.json', 'r') as f:
            facilities = json.load(f)
        with open('data/tips.json', 'r') as f:
            tips = json.load(f)
        return facilities, tips
    except FileNotFoundError:
        st.error("Error: Data files not found. Please make sure 'data/facilities.json' and 'data/tips.json' exist.")
        return None, None
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        return None, None

# Load the data
facilities_data, tips_data = load_data()

# --- 2. Core Engine: Context Retrieval (MVP) ---
# This is our simple keyword-based search engine as per the SDD.
# It searches the 'name', 'type', and 'notes' fields for any of the query words.

def find_facilities(query):
    if not facilities_data:
        return []  # Return empty if data failed to load

    query_words = query.lower().split()
    matches = []

    for facility in facilities_data:
        # Create a searchable text block for each facility
        search_text = f"{facility['name']} {facility['type']} {facility['notes']}".lower()
        
        # Check if any query word is in the search text
        if any(word in search_text for word in query_words):
            matches.append(facility)
            
    return matches

# --- Main Application UI ---
st.title("CityAI – The GenAI Smart City Assistant 🤖")
st.caption("Transforming Urban Life, One AI Conversation at aTime")

# --- Sidebar (with Daily Tip) ---
with st.sidebar:
    st.header("CityAI")
    st.write("Your guide to a smarter city.")
    
    st.subheader("💡 Daily Tip")
    if tips_data:
        # Select and display a random tip
        tip = random.choice(tips_data)
        st.info(f"**{tip['category'].capitalize()}:** {tip['text']}")
    else:
        st.error("Could not load daily tips.")

# --- Test Area for Phase 2 ---
st.subheader("Phase 2 Test: Context Engine")
st.write("Let's test our `find_facilities` function.")

# Create a test input box
test_query = st.text_input("Enter a test query (e.g., 'hospital', 'school', 'civic office')")

if test_query:
    # Run the search
    results = find_facilities(test_query)
    
    if results:
        st.write(f"**Found {len(results)} matching facilities for '{test_query}':**")
        st.json(results) # Display the raw JSON of what it found
    else:
        st.warning(f"No facilities found matching '{test_query}'.")