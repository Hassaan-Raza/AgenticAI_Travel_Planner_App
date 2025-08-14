from crewai import Agent
from TravelTools import search_web_tool
from crewai import LLM
import os

is_local = "localhost" in os.getenv("STREAMLIT_SERVER_BASE_URL", "localhost")
http_referer = "http://localhost:8501" if is_local else "https://your-app-name.streamlit.app"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
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
    goal="Recommend activities based on user interests",
    backstory="Local expert sharing best experiences and hidden gems",
    tools=[search_web_tool],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
    # Add this to guide query formation:
    description="Example searches: 'top sightseeing in New York', 'best food tours NYC'"
)

location_expert = Agent(
    role="Travel Trip Expert",
    goal="Gather helpful information about the city during travel.",
    backstory="""A seasoned traveler who has explored various destinations and knows the ins and outs of travel logistics.""",
    tools=[search_web_tool],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False
)

planner_expert = Agent(
    role="Travel Planning Expert",
    goal="Compile gathered information into a comprehensive travel plan WITHOUT doing additional searches",
    backstory="Professional travel planner who synthesizes information into perfect itineraries",
    tools=[],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
    description=(
        "Combine information from location and guide experts into a cohesive itinerary. "
        "NEVER perform web searches - only use provided context. "
        "Output must include: daily schedule, time allocations, transportation details, and cost estimates."
    )
)