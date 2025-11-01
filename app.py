import streamlit as st
import pandas as pd
import json
import random
import google.generativeai as genai  # Import the Google Gemini SDK

# --- Page Configuration (from UI/UX Doc) ---
st.set_page_config(
    page_title="CityAI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. Smart Data Loading (with Caching) ---
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

facilities_data, tips_data = load_data()

# --- 2. Core Engine: Context Retrieval (MVP) ---
def find_facilities(query):
    if not facilities_data:
        return []
    query_words = query.lower().split()
    matches = []
    for facility in facilities_data:
        search_text = f"{facility['name']} {facility['type']} {facility['notes']}".lower()
        if any(word in search_text for word in query_words):
            matches.append(facility)
    # Return only the top 3 matches to keep the context clean
    return matches[:3]

# --- 3. AI Integration Module (NEW) ---
# This function constructs the prompt and calls the Gemini API.

# Load the API key from st.secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("GEMINI_API_KEY not found. Please add it to your .streamlit/secrets.toml file.")
    st.stop()
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

# Set up the model
generation_config = {
    "temperature": 0.2, # Low temperature for more factual, less creative answers
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config
)

def get_ai_response(query, context):
    # This is the prompt engineering from your PRD/SDD
    # We instruct the AI to be an assistant and *only* use the context.
    # We also give it a fallback message.
    prompt_template = f"""
    You are CityAI, a smart city assistant for an Indian city. 
    Your role is to answer user queries based *only* on the provided context.
    Do not make up information.

    **User Query:**
    {query}

    **Context (List of relevant facilities):**
    {json.dumps(context, indent=2)}

    **Instructions:**
    1.  Analyze the user query and the context.
    2.  If the context contains a relevant facility, provide a helpful answer based on it.
        Present the *best single match* in a structured way.
    3.  If the context is empty or not relevant, respond with: 
        "I'm sorry, I don't have that information in my current city database."
    4.  If the user asks a general question (like 'hello' or 'what is your name?'), 
        answer as a helpful AI assistant.
    """
    
    try:
        response = model.generate_content(prompt_template)
        return response.text
    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return "Sorry, I'm having trouble connecting to the AI service right now."

# --- 4. Custom UI Styling (from UI/UX Doc) (NEW) ---
# We inject custom CSS to create the rounded cards from your design.
st.markdown("""
<style>
    /* Main container for AI responses */
    .ai-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px; /* Rounded corners */
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Subtle shadow */
    }
    .ai-card h3 {
        color: #1F3B6C; /* Deep Blue from your palette */
        margin-top: 0;
    }
    .ai-card p {
        margin-bottom: 4px;
        line-height: 1.5;
    }
    .ai-card strong {
        color: #333;
    }
</style>
""", unsafe_allow_html=True)


# --- 5. Main Application UI & Chat Interface (NEW) ---
st.title("CityAI – The GenAI Smart City Assistant 🤖")
st.caption("Transforming Urban Life, One AI Conversation at aTime")

# --- Sidebar (with Daily Tip) ---
with st.sidebar:
    st.header("CityAI")
    st.image("https://img.icons8.com/color/96/000000/smart-city.png", width=60) # Added a simple icon
    st.write("Your guide to a smarter city.")
    
    st.subheader("💡 Daily Tip")
    if tips_data:
        tip = random.choice(tips_data)
        st.info(f"**{tip['category'].capitalize()}:** {tip['text']}")
    else:
        st.error("Could not load daily tips.")

# --- Chat Interface (NEW) ---
# This is the main chat logic from your PRD.

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Check if content is a dict (our structured card) or str
        if isinstance(message["content"], dict):
            # This is our custom AI card
            st.markdown(f"""
            <div class="ai-card">
                <h3>{message["content"].get("name", "Facility Info")}</h3>
                <p><strong>Address:</strong> {message["content"].get("address", "N/A")}</p>
                <p><strong>Hours:</strong> {message["content"].get("hours", "N/A")}</p>
                <p><strong>Phone:</strong> {message["content"].get("phone", "N/A")}</p>
                <p><strong>Notes:</strong> {message["content"].get("notes", "N/A")}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # This is a plain text message (user or simple AI fallback)
            st.markdown(message["content"])

# Get new user input
if prompt := st.chat_input("Ask about hospitals, schools, or city services..."):
    # 1. Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Show a loading spinner while we work
    with st.spinner("CityAI is thinking..."):
        # 3. This is the RAG pipeline
        # 
        context_data = find_facilities(prompt)
        
        # 4. Get the AI's response
        ai_response_text = get_ai_response(prompt, context_data)
        
        # 5. Check if the AI response *is* one of our facilities
        #    This is a simple way to detect if the AI gave a structured answer
        response_card_data = None
        if context_data and context_data[0]['name'].lower() in ai_response_text.lower():
             # The AI is talking about the facility we found.
             # Let's show the card for the *first* context item.
             response_card_data = context_data[0]

        # 6. Add AI response to history and display it
        if response_card_data:
            # We have a structured card to display
            st.session_state.messages.append({"role": "assistant", "content": response_card_data})
            with st.chat_message("assistant"):
                st.markdown(f"""
                <div class="ai-card">
                    <h3>{response_card_data.get("name", "Facility Info")}</h3>
                    <p><strong>Address:</strong> {response_card_data.get("address", "N/A")}</p>
                    <p><strong>Hours:</strong> {response_card_data.get("hours", "N/A")}</p>
                    <p><strong>Phone:</strong> {response_card_data.get("phone", "N/A")}</p>
                    <p><strong>Notes:</strong> {response_card_data.get("notes", "N/A")}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # We have a simple text response (fallback, or general chat)
            st.session_state.messages.append({"role": "assistant", "content": ai_response_text})
            with st.chat_message("assistant"):
                st.markdown(ai_response_text)