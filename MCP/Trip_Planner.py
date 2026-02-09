import streamlit as st
import requests
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load API keys
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
weather_key = os.getenv("OPENWEATHER_API_KEY")

# Initialize LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=groq_key
)

# ---------------- TOOL ----------------
@tool
def get_weather(city: str) -> str:
    """Get current weather and short forecast for a city."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={weather_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != "200":
        return "Weather data not found."

    current_temp = data["list"][0]["main"]["temp"]
    description = data["list"][0]["weather"][0]["description"]

    forecast = ""
    for i in range(5):
        forecast += f"{data['list'][i]['dt_txt']} - {data['list'][i]['main']['temp']}°C\n"

    return f"Current: {current_temp}°C, {description}\nForecast:\n{forecast}"

# Bind tool to LLM
llm_with_tools = llm.bind_tools([get_weather])

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI Travel Planner.
    When needed, use the weather tool.
    Provide:
    1. Cultural & historical paragraph
    2. Current weather
    3. Suggested travel dates
    4. Flight options (approximate)
    5. Hotel options (approximate)
    6. Day-wise trip plan
    """),
    ("human", "{input}")
])

# Chain
chain = prompt | llm_with_tools | StrOutputParser()

# ---------------- STREAMLIT ----------------
st.title("✈ AI Trip Planner (LangChain + Groq)")

user_input = st.text_input("Enter your trip request")

if st.button("Plan Trip") and user_input:

    # Basic city extraction
    words = user_input.split()
    city = words[-3] if "to" in words else words[-1]

    weather_info = get_weather.invoke(city)

    full_prompt = f"""
User request: {user_input}

Weather information:
{weather_info}

Provide:
1. Cultural & historical significance (1 paragraph)
2. Current weather & forecast
3. Suggested travel dates
4. Flight options (approximate)
5. Hotel options (approximate)
6. Day-wise trip plan
"""

    response = llm.invoke(full_prompt)
    st.write(response.content)

