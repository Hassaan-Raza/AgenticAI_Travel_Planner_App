from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
import re

@tool
def search_web_tool(query: str):
    """Search for travel information with enhanced queries"""
    try:
        # Focus searches on reliable travel sites
        sites = "site:tripadvisor.com OR site:lonelyplanet.com OR site:travelandleisure.com"
        enhanced_query = f"{sites} {query}"

        search = DuckDuckGoSearchResults(
            num_results=5,
            backend="lite",
            safesearch="Moderate"
        )

        results = search.run(enhanced_query)

        # Filter out irrelevant results
        if "no results" in results.lower():
            return search.run(query.split("in")[0])  # Broaden search
        return results

    except Exception as e:
        return f"Search error: {str(e)}. Try simpler terms like 'top attractions in {query.split()[-1]}'"