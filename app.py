import streamlit as st
import os
from pathlib import Path
import sys

# Set BASE_DIR to the current directory
BASE_DIR = Path(__file__).resolve().parent  # Use os.getcwd() if you prefer the working directory

# Swap standard SQLite3 with pysqlite3-binary
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
os.environ["CREWAI_KNOWLEDGE_DISABLED"] = "True"
os.environ["CREWAI_KNOWLEDGE_STORAGE_DISABLED"] = "True"
from TravelAgents import guide_expert, location_expert, planner_expert
from TravelTasks import location_task, guide_task, planner_task
from crewai import Crew, Process
from pdf_gen import generate_pdf
import traceback
from datetime import datetime
import time
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules['pysqlite3']
except ImportError:
    # Fallback to disabling knowledge
    import os
    os.environ["CREWAI_KNOWLEDGE_DISABLED"] = "True"
    os.environ["CREWAI_KNOWLEDGE_STORAGE_DISABLED"] = "True"

# Custom CSS for styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

:root {
    --primary: #2563eb;
    --secondary: #7dd3fc;
    --accent: #f59e0b;
    --light: #f0f9ff;
    --dark: #0c4a6e;
}

* {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.header {
    background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 0 0 20px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 6px 16px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
    border: none;
    color:#1e293b;
}

.btn-primary {
    background: var(--primary) !important;
    border: none !important;
    padding: 0.8rem 2rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

.btn-primary:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 12px rgba(37, 99, 235, 0.3) !important;
}

.input-label {
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 0.5rem;
    display: block;
}

.results-container {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    margin-top: 2rem;
    border-left: 5px solid var(--accent);
    color: black;
}

.footer {
    text-align: center;
    padding: 1.5rem;
    color: #64748b;
    margin-top: 3rem;
    font-size: 0.9rem;
}

.progress-bar {
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
    margin: 1.5rem 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--secondary) 0%, var(--primary) 100%);
    width: 0%;
    transition: width 1s ease-in-out;
}
.custom-status {
    padding: 1.2rem;
    border-radius: 12px;
    margin: 1.5rem 0;
    font-weight: 600;
    font-size: 1.1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.status-spinner {
    background-color: #dbeafe;
    border-left: 5px solid #3b82f6;
    color: #1e40af;
}

.status-success {
    background-color: #dcfce7;
    border-left: 5px solid #22c55e;
    color: #166534;
}

.status-error {
    background-color: #fee2e2;
    border-left: 5px solid #ef4444;
    color: #b91c1c;
}

.stWarning {
    background-color: #fef3c7 !important;
    border-left: 4px solid #f59e0b !important;
    color: #854d0e !important;
}

.stInfo {
    background-color: #dbeafe !important;
    border-left: 4px solid #3b82f6 !important;
    color: #1e40af !important;
}
.stSpinner > div > div {
    color: #1e40af !important;
    font-weight: 600 !important;
    font-size: 1.2rem !important;
}

.stSpinner > div > div::after {
    content: " ✈️"; /* Add plane emoji for visual interest */
    animation: plane 2s infinite;
}

@keyframes plane {
    0% { content: " ✈️"; }
    33% { content: " 🌍"; }
    66% { content: " 🗺️"; }
    100% { content: " ✈️"; }
}

/* Transport selection styling */
.transport-option {
    display: flex;
    align-items: center;
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
    cursor: pointer;
    transition: all 0.2s;
}

.transport-option:hover {
    background-color: #f1f5f9;
}

.transport-option.selected {
    background-color: #dbeafe;
    border: 2px solid #3b82f6;
}

.transport-emoji {
    font-size: 24px;
    margin-right: 10px;
}

.transport-label {
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)
st.set_page_config(
    page_title="Wander AI Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Initialize session state for plan visibility
if 'show_plan' not in st.session_state:
    st.session_state.show_plan = False
if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'transport_mode' not in st.session_state:
    st.session_state.transport_mode = "plane"
if 'show_plan_button' not in st.session_state:
    st.session_state.show_plan_button = False

# App Header
st.markdown(
    '<div class="header"><h1 style="margin:0;">✈️ Wander AI Planner</h1><p>Your personal AI travel concierge</p></div>',
    unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class="card">
    <h3>✨ Plan Your Perfect Getaway</h3>
    <p>Let our AI travel experts craft your dream itinerary. We'll handle everything from accommodations to activities!</p>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem;">
        <div style="text-align: center;">
            <div style="font-size: 2rem;">🏨</div>
            <div>Accommodations</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2rem;">🍽️</div>
            <div>Dining</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2rem;">🗺️</div>
            <div>Itinerary</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Travel Form
with st.form("travel_form"):
    st.markdown('<div class="card"><h3>📝 Trip Details</h3></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="input-label">Departure City</p>', unsafe_allow_html=True)
        from_city = st.text_input(
            "Departure City",
            placeholder="e.g., London, Paris, Tokyo",
            label_visibility="collapsed"
        )

        st.markdown('<p class="input-label">Travel Dates</p>', unsafe_allow_html=True)
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            date_from = st.date_input("Start Date", datetime(2025, 8, 13), label_visibility="collapsed")
        with date_col2:
            date_to = st.date_input("End Date", datetime(2025, 8, 20), label_visibility="collapsed")

    with col2:
        st.markdown('<p class="input-label">Destination City</p>', unsafe_allow_html=True)
        destination_city = st.text_input(
            "Destination City",
            placeholder="e.g., Rome, New York, Bali",
            label_visibility="collapsed"
        )

        st.markdown('<p class="input-label">Travel Interests</p>', unsafe_allow_html=True)
        interests = st.text_area(
            "Travel Interests",
            placeholder="e.g., art museums, street food, hiking, photography",
            label_visibility="collapsed",
            height=100
        )

    # Transportation mode selection
    st.markdown('<p class="input-label">Transportation Mode</p>', unsafe_allow_html=True)
    transport_options = ["✈️ Plane", "🚗 Car", "🚲 Bike", "🚆 Train", "🚌 Bus"]
    transport = st.radio(
        "Transportation Mode",
        transport_options,
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    # Extract just the mode name for the backend
    transport_mode = transport.split(" ")[1].lower()

    st.markdown('<div class="progress-bar"><div class="progress-fill" id="progress"></div></div>',
                unsafe_allow_html=True)

    submitted = st.form_submit_button("🚀 Generate Travel Plan", type="primary", use_container_width=True)

# Results Section
if submitted:
    if not all([from_city, destination_city, date_from, date_to, interests]):
        st.markdown(
            '<div class="custom-status status-error">⚠️ Please complete all fields before generating your travel plan.</div>',
            unsafe_allow_html=True
        )
    else:
        # Animated progress bar
        progress_bar = st.empty()
        for percent in range(0, 101, 5):
            progress_bar.markdown(
                f'<div class="progress-bar"><div class="progress-fill" style="width:{percent}%"></div></div>',
                unsafe_allow_html=True
            )
            time.sleep(0.1)

        status_container = st.empty()
        with st.spinner("🧠 AI travel experts are crafting your perfect itinerary..."):
            try:
                # Initialize Tasks
                loc_task = location_task(location_expert, from_city, destination_city, date_from, date_to,
                                         transport_mode)
                guid_task = guide_task(guide_expert, destination_city, interests, date_from, date_to, transport_mode)
                plan_task = planner_task([loc_task, guid_task], planner_expert, from_city, destination_city, interests,
                                         date_from, date_to, transport_mode)

                # Define Crew
                crew = Crew(
                    agents=[location_expert, guide_expert, planner_expert],
                    tasks=[loc_task, guid_task, plan_task],
                    process=Process.sequential,
                    full_output=True,
                    verbose=True,
                )

                # Run Crew AI
                result = crew.kickoff()
                travel_plan_text = str(result)

                # Store the result in session state
                st.session_state.travel_plan = travel_plan_text
                st.session_state.transport_mode = transport_mode

                # Display Results
                status_container.markdown(
                    '<div class="custom-status status-success">✅ Your personalized travel plan is ready!</div>',
                    unsafe_allow_html=True
                )

                # Show the "Show Plan" button
                st.session_state.show_plan_button = True

            except Exception as e:
                status_container.markdown(
                    f'<div class="custom-status status-error">⚠️ We encountered an error: {str(e)}</div>',
                    unsafe_allow_html=True
                )
                st.info("Please try again or adjust your inputs")

# Show the "Show Plan" button if we have a plan
if hasattr(st.session_state, 'show_plan_button') and st.session_state.show_plan_button:
    if st.button("👀 Show Travel Plan", use_container_width=True):
        st.session_state.show_plan = True
        st.session_state.show_plan_button = False
        st.rerun()

# Display the plan if it's supposed to be shown
if hasattr(st.session_state, 'show_plan') and st.session_state.show_plan and st.session_state.travel_plan:
    try:
        # Generate PDF
        pdf_bytes = generate_pdf(st.session_state.travel_plan, st.session_state.transport_mode)

        # Display PDF download button
        st.download_button(
            label="📄 Download PDF Travel Plan",
            data=pdf_bytes,
            file_name=f"{destination_city}_Travel_Plan.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # Show the plan preview
        st.markdown(f'<div class="results-container">{st.session_state.travel_plan}</div>', unsafe_allow_html=True)

    except Exception as pdf_error:
        st.markdown(
            f'<div class="custom-status status-error">⚠️ PDF generation failed: {str(pdf_error)}</div>',
            unsafe_allow_html=True
        )

        # Text fallback
        st.markdown(f'<div class="results-container">{st.session_state.travel_plan}</div>', unsafe_allow_html=True)
        st.download_button(
            label="💾 Download Text Travel Plan",
            data=st.session_state.travel_plan,
            file_name=f"{destination_city}_Travel_Plan.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer with the requested message
st.markdown("""
<div class="footer">
    <p>Made with ❤️ using Streamlit & CrewAI | Wander AI Planner © 2025</p>
    <p style="color: #007a4d; font-weight: bold; margin-top: 10px;">🇵🇸 Free Palestine</p>
</div>
""", unsafe_allow_html=True)