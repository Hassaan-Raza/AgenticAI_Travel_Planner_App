from crewai import Task


def location_task(agent, from_city, destination_city, date_from, date_to, transport):
    # Determine transportation research based on mode
    transport_research = ""
    if transport.lower() == 'plane':
        transport_research = "- Research airport transportation options"
    else:
        transport_research = f"- Research {transport} routes from {from_city} to {destination_city} including distance, estimated travel time, and best routes"

    return Task(
        description=f"""
        Research and compile travel information for {destination_city}:
        - Find 3 budget and 3 luxury hotels with prices
        {transport_research}
        - Check visa requirements for travelers from {from_city}
        - Get weather forecast for {date_from} to {date_to}
        - Find local events during travel dates

        Travel details:
        - From: {from_city}
        - To: {destination_city}
        - Dates: {date_from} to {date_to}
        - Mode of transport: {transport}

        IMPORTANT: 
        - Use specific search terms like "best hotels in New York August 2025"
        - For non-plane transportation, search for "best {transport} routes from {from_city} to {destination_city}"
        - Format all prices in USD
        """,
        expected_output="Markdown report with bullet points and prices including transportation details",
        agent=agent,
        output_file='city_report.md'
    )


def guide_task(agent, destination_city, interests, date_from, date_to, transport):
    return Task(
        description=f"""Tailored to the traveler's personal {interests}, this task focuses on creating an engaging and informative guide to the city's attractions. It involves identifying cultural landmarks, historical spots, entertainment venues, dining experiences, and outdoor activities that align with the user's preferences such {interests}. The guide also highlights seasonal events and festivals that might be of interest during the traveler's visit.

        Additionally, consider transportation mode ({transport}) when recommending activities and provide appropriate local transportation tips.

        Destination city: {destination_city}
        Interests: {interests}
        Arrival Date: {date_from}
        Departure Date: {date_to}
        Mode of transport: {transport}
        """,
        expected_output=f"""An interactive markdown report that presents a personalized itinerary of activities and attractions, complete with descriptions, locations, and any necessary reservations or tickets. Include transportation recommendations between activities based on the travel mode {transport}.
        """,
        agent=agent,
        output_file='guide_report.txt'
    )


def planner_task(context, agent, from_city, destination_city, interests, date_from, date_to, transport):
    # Add transportation-specific instructions
    transport_instructions = ""
    if transport.lower() != 'plane':
        transport_instructions = (
            f"8. Since traveler is using {transport}, provide detailed route information from {from_city} to {destination_city}:\n"
            f"   - Best routes and alternative options\n"
            f"   - Estimated travel time and distance\n"
            f"   - Recommended stops along the way\n"
            f"   - Any special considerations for this mode of transport\n"
        )

    return Task(
        description=(
            f"Create FINAL TRAVEL PLAN for {destination_city} using ONLY information from location and guide experts:\n"
            f"1. Write 3-paragraph city introduction\n"
            f"2. Create day-by-day itinerary from {date_from} to {date_to}\n"
            f"3. Include time slots (9:00 AM, 2:00 PM, etc.) for each activity\n"
            f"4. Add transportation details between locations\n"
            f"5. Include cost estimates for each day\n"
            f"6. Format in markdown with emojis\n"
            f"7. Tailor recommendations to traveler's interests: {interests}\n"
            f"{transport_instructions}\n"
            f"IMPORTANT: DO NOT SEARCH WEB - USE ONLY PROVIDED CONTEXT"
        ),
        expected_output=(
                "# 🌆 Welcome to {destination_city}\n"
                "[3-paragraph introduction]\n\n"
                "# 🗓️ Daily Itinerary\n"
                "## Day 1: [Date]\n"
                "⏰ 9:00 AM: [Activity 1]\n"
                "🚕 Transportation: [Details]\n"
                "💵 Cost: [Amount]\n\n"
                "⏰ 12:00 PM: [Lunch at restaurant]\n"
                "...\n\n"
                "# 🚗 Transportation Details\n" +
                (f"[Detailed {transport} route information from {from_city} to {destination_city}]"
                 if transport.lower() != 'plane' else "[Flight information]")
        ),
        context=context,
        agent=agent,
        output_file='travel_plan.md'
    )