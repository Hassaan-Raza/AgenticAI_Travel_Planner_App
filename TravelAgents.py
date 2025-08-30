from crewai import Agent
import os
import streamlit as st
os.environ["CREWAI_KNOWLEDGE_DISABLED"] = "True"
os.environ["CREWAI_KNOWLEDGE_STORAGE_DISABLED"] = "True"
from TravelTools import search_web_tool
from crewai import LLM

is_local = "localhost" in os.getenv("STREAMLIT_SERVER_BASE_URL", "localhost")
http_referer = "http://localhost:8501" if is_local else "https://agenticaitravelplannerapp-mq5sc4yvgzbj5bvzckwfdv.streamlit.app"

OPENROUTER_API_KEY =  os.getenv("OPENROUTER_API_KEY") or st.secrets["openrouter"]["api_key"]  # No fallback value!

if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY environment variable")

llm = LLM(
    model="openrouter/mistralai/mixtral-8x7b-instruct",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.7,
    headers={
        "HTTP-Referer": http_referer,
        "X-Title": "AI Travel Planner",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }
)

guide_expert = Agent(
    role="City Local Guide Expert",
    goal="Recommend activities based on user interests and transportation mode",
    backstory="Local expert sharing best experiences and hidden gems, with special knowledge of transportation options",
    tools=[search_web_tool],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
    description=(
        "Example searches: 'top sightseeing in New York', 'best food tours NYC', "
        "'bike-friendly activities in Paris', 'car routes between cities', "
        "'scenic routes from [city] to [city] by [transport]'"
    )
)

location_expert = Agent(
    role="Travel Trip and Route Expert",
    goal="Gather helpful information about the city and plan transportation routes",
    backstory="""A seasoned traveler and route planner who has explored various destinations and knows the ins and outs of travel logistics for all transportation modes.""",
    tools=[search_web_tool],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
    description=(
        "Expert in finding transportation options including flights, car routes, bike paths, and public transport. "
        "Example searches: 'hotels in [city]', 'weather [city] [dates]', "
        "'driving route from [city] to [city]', 'bike routes between [cities]', "
        "'public transport options [city]'"
    )
)

planner_expert = Agent(
    role="Travel Planning and Route Synthesis Expert",
    goal="Compile gathered information into a comprehensive travel plan with transportation details",
    backstory="Professional travel planner who specializes in creating multimodal itineraries with detailed transportation planning",
    tools=[],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
    description=(
        "Combine information from location and guide experts into a cohesive itinerary. "
        "Specialize in creating detailed transportation plans for all modes (plane, car, bike, etc.). "
        "NEVER perform web searches - only use provided context. "
        "Output must include: daily schedule, time allocations, transportation details, route maps when applicable, and cost estimates."
    )
)