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
    .main {
        background-color: #0e1117;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #f0f0f0;
    }
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

with st.sidebar:
    st.header("API Configuration")
    st.markdown("[Get Exa API Key](# API Playground URL: https://dashboard.exa.ai/playground) 🔑")
    exa_api_key = st.text_input("Exa API Key", type="password")

    st.markdown("[Get Groq API Key](# GROQ API Key: https://console.groq.com/keys) 🔑")
    groq_api_key = st.text_input("Groq API Key", type="password")
    
    st.header("Model Settings")
    model_name = st.selectbox(
        "Select Model",
        ["mixtral-8x7b-32768"],
        index=0
    )
    
    st.header("About")
    st.markdown("""
    This app uses AI to recommend movies based on your preferences. 
    It leverages Groq for the language model and Exa for search capabilities.
    
    Enter your preferences, and the AI will suggest personalized movie recommendations!
    """)

st.header("Enter Your Movie Preferences")


col1, col2 = st.columns(2)

with col1:
    favorite_movies = st.text_area("Your favorite movies (comma separated)", 
                                 placeholder="e.g., The Godfather, Inception, The Shawshank Redemption")
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

additional_preferences = st.text_area("Any Additional Preferences", 
                                    placeholder="e.g., foreign films, specific directors, themes, or elements you're looking for")


def get_movie_recommendations(query_text):
    if not exa_api_key or not groq_api_key:
        st.error("Please provide both Exa and Groq API keys in the sidebar.")
        return None
    
    movie_recommendation_agent = Agent( 
        name="Movie Recommendation Agent",
        model=Groq(name=model_name, api_key=groq_api_key), 
        tools=[ExaTools(api_key=exa_api_key)],
        description=dedent(
            """
            🎬 You are a **Movie Recommendation Agent**! Your mission is to help users discover their next favorite movies based on their preferences.  

            🎥 **Your Role as a Movie Expert**  
            - Analyze user preferences to recommend **personalized movie suggestions**.  
            - Curate recommendations using a mix of **classic hits, hidden gems, and trending movies**.  
            - Ensure each suggestion is **relevant, diverse, and highly rated**.  
            - Provide **up-to-date information**, including cast, director, runtime, and content advisory.  
            - Highlight **where to watch** and suggest **upcoming releases**.  

            🍿 **Your Recommendations Should Include:**  
            - 🎞️ **Title & Release Year**  
            - 🎭 **Genre & Subgenres** (with emoji indicators)  
            - ⭐ **IMDb Rating** (Focus on 7.5+ rated films)  
            - ⏳ **Runtime & Primary Language**  
            - 📖 **Engaging Plot Summary**  
            - ⚠️ **Content Advisory / Age Rating**  
            - 🎬 **Notable Cast & Director**  

            📌 **Presentation Guidelines:**  
            - Use **clear Markdown formatting** for better readability.  
            - Organize recommendations in a **structured table**.  
            - **Group similar movies together** for better discovery.  
            - Provide **at least 5 personalized recommendations per query**.  
            - Offer a **brief explanation** for why each movie was selected.  
            """
        ),
        instructions=dedent(
            """
            ## 🎬 Approach for Generating Recommendations

            ### 1. **Analysis Phase**
            - Interpret user preferences based on input.
            - Analyze favorite movies for themes, styles, and patterns.
            - Consider specific user requirements (e.g., genre, rating, language, mood).

            ### 2. **Search & Curation**
            - Utilize Exa to search for relevant movie options.
            - Ensure variety in recommendations (mix of classics, hidden gems, and trending titles).
            - Verify that movie details are up-to-date and accurate.

            ### 3. **Detailed Information for Each Recommendation**
            Each movie recommendation should include:
            - 🎞️ **Title & Release Year**  
            - 🎭 **Genre & Subgenres** (with emoji indicators)  
            - ⭐ **IMDb Rating** (Focus on 7.5+ rated films)  
            - ⏳ **Runtime & Primary Language**  
            - 📖 **Brief, Engaging Plot Summary**  
            - ⚠️ **Content Advisory / Age Rating**  
            - 🎬 **Notable Cast & Director**  

            ### 4. **Additional Features**
            - Include official trailers when available.
            - Suggest upcoming releases in similar genres.
            - Mention streaming availability when possible.

            ### 🎨 **Presentation Style**
            - Format output using **clear Markdown structure**.
            - Present **main recommendations in a structured table**.
            - Group similar movies together for **easy browsing**.
            - Use **emoji indicators** to visually represent genres (e.g., 🎭 *Drama*, 🎬 *Action*, 🎪 *Adventure*).
            - Provide a **minimum of 5 recommendations per query**.
            - Offer a **brief explanation** of why each movie was recommended.
            """
        ),
        markdown=True,
    )
    
    # Generate response using the run method instead of generate
    response = movie_recommendation_agent.run(query_text)
    return response.content

# Build the search query based on user inputs
def build_query():
    query_parts = []
    
    if favorite_movies:
        query_parts.append(f"I like movies such as {favorite_movies}")
    
    if preferred_genres:
        genres_str = ", ".join(preferred_genres)
        query_parts.append(f"I prefer {genres_str} genres")
    
    if mood != "Any":
        query_parts.append(f"I'm in a {mood.lower()} mood")
    
    if preferred_decade != "Any":
        query_parts.append(f"I prefer movies from the {preferred_decade}")
    
    if additional_preferences:
        query_parts.append(additional_preferences)
    
    return "Recommend movies based on these preferences: " + ". ".join(query_parts)

# Search button
if st.button("Get Movie Recommendations", type="primary"):
    if not favorite_movies and not preferred_genres and not additional_preferences:
        st.warning("Please provide some movie preferences for better recommendations.")
    else:
        query = build_query()
        
        with st.spinner("Agent 🤖 isFinding the perfect movies for you..."):
            st.info(f"Searching for: {query}")
            
            # Get recommendations
            with st.container():
                recommendations = get_movie_recommendations(query)
                if recommendations:
                    st.markdown("---")
                    st.markdown(recommendations)
                    st.markdown("---")
                    st.download_button(
                        label="Download Recommendations",
                        data=recommendations,
                        file_name="movie_recommendations.md",
                        mime="text/markdown",
                    )


st.markdown("---")
