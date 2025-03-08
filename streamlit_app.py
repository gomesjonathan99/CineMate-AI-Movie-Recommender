import os
import streamlit as st
from textwrap import dedent
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.exa import ExaTools
from dotenv import load_dotenv

load_dotenv(override=True)

st.set_page_config(
    page_title="Movie Recommendation App",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { max-width: 1200px; margin: 0 auto; }
    h1, h2, h3 { color: #f0f0f0; }
    .recommendation {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 Movie Recommendation App")
st.markdown("Discover your next favorite movie based on your preferences!")

# Sidebar for API Configuration
with st.sidebar:
    st.header("API Configuration")
    st.markdown("[🔑 Get Exa API Key](https://dashboard.exa.ai/playground)")
    exa_api_key = st.text_input("Exa API Key", type="password")

    st.markdown("[🔑 Get Groq API Key](https://console.groq.com/keys)")
    groq_api_key = st.text_input("Groq API Key", type="password")

    st.header("Model Settings")
    model_name = st.selectbox("Select Model", ["mixtral-8x7b-32768"], index=0)

    st.header("About")
    st.markdown("""
    This app uses AI to recommend movies based on your preferences.  
    It leverages **Groq** for the language model and **Exa** for search capabilities.  
    Enter your preferences, and the AI will suggest **personalized movie recommendations!** 🎥
    """)

# User input section
st.header("🎥 Enter Your Movie Preferences")

col1, col2 = st.columns(2)

with col1:
    favorite_movies = st.text_area(
        "Your favorite movies (comma separated)", 
        placeholder="e.g., The Godfather, Inception, The Shawshank Redemption"
    )
    
    preferred_genres = st.multiselect(
        "Preferred Genres",
        ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", 
         "Drama", "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller"],
        []
    )

with col2:
    mood = st.selectbox(
        "Current Mood",
        ["Any", "Happy", "Thoughtful", "Excited", "Relaxed", "Nostalgic", "Inspired"],
        index=0
    )

    decade_options = ["Any"] + [f"{i}s" for i in range(1920, 2030, 10)]
    preferred_decade = st.selectbox("Preferred Decade", decade_options, index=0)

additional_preferences = st.text_area(
    "Any Additional Preferences", 
    placeholder="e.g., foreign films, specific directors, themes, or elements you're looking for"
)

# Function to get movie recommendations
def get_movie_recommendations(query_text):
    if not exa_api_key or not groq_api_key:
        st.error("❌ Please provide both Exa and Groq API keys in the sidebar.")
        return None
    
    movie_recommendation_agent = Agent( 
        name="Movie Recommendation Agent",
        model=Groq(name=model_name, api_key=groq_api_key), 
        tools=[ExaTools(api_key=exa_api_key)],
        description=dedent(
            """
            🎬 You are a **Movie Recommendation Agent**!  
            Your mission is to help users discover their next favorite movies.  

            ### Your Role as a Movie Expert  
            - 🎥 **Analyze user preferences** to recommend personalized movies.  
            - 🎭 **Curate a mix of classics, hidden gems, and trending titles.**  
            - ⭐ Focus on **highly-rated** (7.5+ IMDb) and relevant films.  
            - ⏳ Provide **runtime, cast, director, and content advisory**.  
            - 📌 Mention **streaming availability & upcoming releases**.  

            ### Formatting Guidelines  
            - Use **clear Markdown formatting** 📜.  
            - Present **structured movie recommendations** (Title, Year, Genre, IMDb rating, etc.).  
            - Provide at least **5 personalized recommendations** per query.  
            """
        ),
        instructions=dedent(
            """
            ## 🎬 How to Recommend Movies  

            **1️⃣ Analyze User Preferences**  
            - Extract themes, styles, and genres from input.  
            - Identify trending & classic movies that match.  

            **2️⃣ Curate a Balanced List**  
            - Use **Exa** to find relevant movies.  
            - Ensure a mix of genres & styles.  

            **3️⃣ Provide Detailed Information**  
            Each movie should include:  
            - 🎞️ **Title & Year**  
            - 🎭 **Genre & IMDb Rating**  
            - ⏳ **Runtime & Language**  
            - 📖 **Engaging Plot Summary**  
            - 🎬 **Notable Cast & Director**  
            - ⚠️ **Content Advisory**  

            **4️⃣ Format Recommendations Clearly**  
            - Use bullet points & emojis.  
            - Provide a **minimum of 5 recommendations**.  
            """
        ),
        markdown=True,
    )
    
    response = movie_recommendation_agent.run(query_text)
    return response.content

# Build query based on user input
def build_query():
    query_parts = []
    
    if favorite_movies:
        query_parts.append(f"I like movies such as {favorite_movies}.")
    
    if preferred_genres:
        genres_str = ", ".join(preferred_genres)
        query_parts.append(f"I prefer {genres_str} genres.")
    
    if mood != "Any":
        query_parts.append(f"I'm in a {mood.lower()} mood.")
    
    if preferred_decade != "Any":
        query_parts.append(f"I prefer movies from the {preferred_decade}.")
    
    if additional_preferences:
        query_parts.append(f"Additional preferences: {additional_preferences}")
    
    return "Recommend movies based on these preferences: " + " ".join(query_parts)

# Generate movie recommendations
if st.button("🎬 Get Movie Recommendations", type="primary"):
    if not favorite_movies and not preferred_genres and not additional_preferences:
        st.warning("⚠️ Please provide some movie preferences for better recommendations.")
    else:
        query = build_query()
        
        with st.spinner("🤖 Finding the perfect movies for you..."):
            st.info(f"🔍 Searching for: {query}")
            
            # Fetch recommendations
            with st.container():
                recommendations = get_movie_recommendations(query)
                if recommendations:
                    st.markdown("---")
                    st.markdown(recommendations)
                    st.markdown("---")
                    st.download_button(
                        label="⬇️ Download Recommendations",
                        data=recommendations,
                        file_name="movie_recommendations.md",
                        mime="text/markdown",
                    )

st.markdown("---")
