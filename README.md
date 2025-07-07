💪 Ultimate Fitness Planner — Enterprise Wellness Agent

An Agentic AI-Powered Web App for Employee Wellness
Designed for the Future of Work | Built with Streamlit, Firebase, Groq, and Fetch.ai | Deployment-Ready Architecture

🌟 Overview

Ultimate Fitness Planner is a smart, agent-driven wellness platform built for enterprise teams. It empowers organizations to improve employee health and productivity using autonomous AI planning tools and a proactive wellness assistant that delivers personalized motivational nudges — all without user prompts.

This isn’t just another fitness tracker. It’s your always-on, intelligent wellness agent.

🚀 Why It’s Different — Agentic Workflows in Action

✅ Enterprise-Ready
Designed for organizations and departments: HR, Marketing, Ops, and more

Track individual progress and organization-wide participation from a single dashboard

🤖 Truly Agentic

Built with Fetch.ai's uAgents framework — not a chatbot

Periodically runs checks in the background

Detects inactivity and sends motivational nudges automatically

Runs independently — zero user prompts required

🧠 Built for the Future of Work

Supports healthier habits, reduces burnout, and boosts team morale

Encourages nutrition, movement, and mental well-being

Autonomous AI as a well-being co-pilot for modern teams

🛠️ Tech Stack

Layer	Technology
Frontend	Streamlit
Backend / DB	Python + Firebase Firestore
AI Model	Groq running LLaMA 3 (8B)
Agent Layer	Fetch.ai’s uAgents
Deployment	Locally supported (Vultr Deployment Planned)

🧩 Key Features

📋 Personalized Body Metrics
Users input weight, height, age, and goals

Automatically calculates BMI, BMR, and body fat %

🥗 Diet Planner
Personalized AI-generated meal plans

Full-day meal suggestions and recipes

🏋️ Workout Planner
Suggests home/gym workouts based on fitness level, body type, and equipment

📚 Exercise Library
Manual + AI-powered exercise search

Categorized by muscle groups

📊 Dashboard
Weekly summaries and quick actions

Visual progress tracking for motivation

🔔 Wellness Nudge Agent (The Game Changer)
Agent runs hourly or daily

Detects inactivity in Firestore logs (e.g., 3+ days without exercise)

Groq + LLaMA 3 generate personalized motivational nudges

Sends messages automatically to the frontend

🧠 Under the Hood: How the Agent Works
Component	Role
uAgent (Fetch.ai)	Autonomous agent — performs checks and sends nudges
Firestore (Firebase)	Stores user data, metrics, and logs
Groq + LLaMA 3	Generates creative, personalized motivational messages

Workflow:

Agent wakes on schedule

Scans for inactivity

If found, requests Groq to generate a message

Sends it back to the frontend automatically

⚙️ Setup & Installation

git clone https://github.com/Aatka-Saleem/fitness_testing.git

cd fitness_testing

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

🔐 Configuration
.streamlit/secrets.toml: Firebase credentials

.env:
GROQ_API_KEY=your_groq_api_key  
FITNESS_UAGENT_ADDRESS=your_agent_wallet_address  

🏁 Run the App

Terminal 1:

python run_fetch_agent.py

Terminal 2:


streamlit run streamlit_app.py

☁️ Deployment Notes
⚠️ Full Vultr Deployment Coming Soon

While the platform is fully functional and tested in local environments, deployment to Vultr cloud infrastructure is planned for future phases. The architecture is built for cloud readiness, but final deployment steps are pending.

🚧 Future Improvements
We have a strong roadmap for enhancing the platform:

🔐 Secure User Onboarding
Admin-controlled invites to prevent unauthorized access.

🛡️ Granular Admin Permissions
Advanced role management within organizations.

🏆 Team-Based Leaderboards
Showcasing anonymized performance data to promote healthy competition.

⚡ Advanced Agent Triggers
Nudge not just inactivity, but also:

Streak recognition

Energy-based meal suggestions

🌍 Full Vultr Deployment
Bringing the platform to production-ready hosting for global access.

👥 Built For
HR & People Teams

Startups building wellness-first cultures

Enterprise wellness programs seeking AI automation

Hackathons and future-of-work showcases

🙌 Team & Acknowledgments
Built for the Raise Your Hackathon (Vultr x Agentic Workflows)
Special thanks to Fetch.ai, Groq, Streamlit, and Vultr

Team Leader:
AATKA

Team Members:
AREEBA SHAKEEL
KHOLAH REHAN
NAVEERA SHARIF
SYEDA ANEEQA FATIMA
