import streamlit as st
import openai
import requests
import json
import os


# OpenAI API Key
#OPENAI_API_KEY = " "
import openai

openai.api_key = " "


# Function to interact with OpenAI API
def chat_with_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful AI travel assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# Function to get real-time travel suggestions
def get_travel_suggestions(destination, interest):
    search_query = f"Top {interest} places in {destination}"
    TAVILY_API_KEY = os.getenv("api key")  # Set this in your system environment variables
    search_url = f"https://api.tavily.com/search?query={search_query}&api_key={TAVILY_API_KEY}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        return [result['title'] for result in data.get('results', [])][:5]
    return ["No data available"]

# Streamlit UI
st.title("AI Travel Planner")

# User Inputs
budget = st.selectbox("Select Budget:", ["Low", "Moderate", "Luxury"])
destination = st.text_input("Enter Destination:")
duration = st.number_input("Trip Duration (in days):", min_value=1, max_value=30)
interests = st.multiselect("Select Interests:", ["History", "Food", "Nature", "Adventure", "Hidden Gems"])

diet = st.selectbox("Dietary Preferences:", ["No preference", "Vegetarian", "Vegan", "Halal", "Kosher"])
stay = st.selectbox("Accommodation Type:", ["Budget", "Mid-range", "Luxury"])

if st.button("Generate Itinerary"):
    if not destination:
        st.error("Please enter a destination.")
    else:
        # Generate suggestions
        activities = {}
        for interest in interests:
            activities[interest] = get_travel_suggestions(destination, interest)
        
        # Prepare the prompt
        user_details = f"Destination: {destination}, Budget: {budget}, Duration: {duration} days, Interests: {', '.join(interests)}, Dietary: {diet}, Stay: {stay}"
        itinerary_prompt = f"Create a detailed {duration}-day travel itinerary for {destination}. Interests: {', '.join(interests)}. Budget: {budget}. Stay: {stay}. Dietary: {diet}. Include hidden gems and food recommendations."
        itinerary = chat_with_openai(itinerary_prompt)
        
        # Display output
        st.subheader("Recommended Activities:")
        for interest, places in activities.items():
            st.write(f"**{interest}:** {', '.join(places)}")
        
        st.subheader("Day-by-Day Itinerary:")
        st.write(itinerary)
