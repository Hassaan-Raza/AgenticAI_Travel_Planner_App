from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
import re


@tool
def search_web_tool(query: str):
    """Search for travel information with enhanced queries, including route planning"""
    try:
        # Check if this is a route planning query
        route_keywords = ['route', 'driving', 'biking', 'cycling', 'by car', 'by bike', 'road trip', 'directions']
        is_route_query = any(keyword in query.lower() for keyword in route_keywords)

        # Focus searches on appropriate sites based on query type
        if is_route_query:
            # For route planning, use mapping and transportation sites
            sites = "site:google.com/maps OR site:mapquest.com OR site:rome2rio.com OR site:waze.com"
            enhanced_query = f"{sites} {query}"
        else:
            # For general travel info, use travel sites
            sites = "site:tripadvisor.com OR site:lonelyplanet.com OR site:travelandleisure.com OR site:booking.com"
            enhanced_query = f"{sites} {query}"

        search = DuckDuckGoSearchResults(
            num_results=7 if is_route_query else 5,  # More results for routes
            backend="lite",
            safesearch="Moderate"
        )

        results = search.run(enhanced_query)

        # If no results found with site restrictions, try broader search
        if "no results" in results.lower() or "no good" in results.lower():
            # For route queries, try specific mapping terms
            if is_route_query:
                fallback_query = f"best {query} route map directions"
            else:
                fallback_query = query.split("in")[0] if "in" in query else query

            return search.run(fallback_query)

        return results

    except Exception as e:
        error_msg = f"Search error: {str(e)}. "
        if "route" in query.lower() or "directions" in query.lower():
            error_msg += "Try simpler terms like 'driving from [city] to [city]' or 'bike routes between [cities]'"
        else:
            error_msg += f"Try simpler terms like 'top attractions in {query.split()[-1]}'"
        return error_msg