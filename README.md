💪 Ultimate Fitness Planner — Enterprise Wellness Agent
An Agentic AI-Powered Web App for Employee Wellness
Designed for the Future of Work | Built with Streamlit, Firebase, Groq, and Fetch.ai | Deployed on Vultr

🌟 Overview
Ultimate Fitness Planner is a web-based wellness platform purpose-built for enterprise teams. It empowers organizations to enhance employee health and productivity using AI-powered planning tools and a proactive autonomous agent that delivers personalized motivational nudges.

This isn't just another fitness app — it's a smart, self-driving wellness assistant. It uses an agentic architecture to reason, plan, and act on behalf of employees, saving time and driving healthier workplace behaviors with minimal input.

🚀 Why It’s Different — Agentic Workflows in Action
✅ Enterprise-Ready
Designed with teams in mind: Employees can track progress, while HR or admins can monitor participation and engagement.

Supports wellness at scale across departments: marketing, ops, HR, and more.

🤖 Truly Agentic
Not a chatbot. A real autonomous agent built using Fetch.ai’s uAgents framework.
Periodically scans user activity in the background.
Detects inactivity and automatically sends motivational nudges using LLM-generated messages.
Requires zero user prompt — just let it run.

🧠 Future of Work-Focused
Promotes healthy habits, reduces burnout, and boosts morale.
A smart companion that encourages movement, nutrition, and personal progress without micromanagement.
Sets the stage for AI to support holistic employee well-being in tomorrow’s workplace.

🛠️ Tech Stack
Layer	Technology
Frontend	Streamlit
Backend / DB	Python + Firebase Firestore
AI Model	Groq running LLaMA 3 (8B)
Autonomous Agent	Fetch.ai’s uAgents
Deployment	Deployed on Vultr (Cloud Hosting)

🧩 Key Features
📋 Personalized Body Metrics
Users input weight, height, age, and fitness goals.

Calculates BMI, BMR, and body fat %, used by all planners.

🥗 Diet Planner
Generates AI-powered personalized meal plans based on goals (e.g. weight loss, muscle gain).

Includes full-day meal suggestions and recipes.

🏋️ Workout Planner
Suggests workouts based on user's body type, fitness goals, and available equipment.

Supports home and gym setups.

📚 Exercise Library
Manual exercise list categorized by muscle group.

AI-powered search to suggest new exercises.

📊 Dashboard
Weekly summaries, quick actions, and performance insights.

Central place to view progress and navigate features.

🔔 Wellness Nudge Agent (The Game Changer)
Autonomous agent runs on a schedule (e.g., every hour).
Checks Firestore logs to detect user inactivity (e.g., no workouts in 3+ days).

Uses Groq + LLaMA 3 to generate friendly motivational messages.

Sends nudges back to the user — fully automated.

🧠 How the Agent Works — Under the Hood
Component	Role
Fetch.ai Agent (uAgents)	The autonomous executor. Runs scheduled checks, initiates nudges, and communicates via messages.
Firestore (Firebase)	Stores all user logs, body metrics, and session data. Acts as the agent’s “memory.”
Groq + LLaMA 3	The creative mind. Given a prompt (e.g., user inactivity), it writes personalized motivational content.

Workflow:
The agent wakes up (on a timer).
It scans the Firestore database for inactive users.
If inactivity is found, it requests Groq to generate a motivational nudge.
The message is sent to the frontend or notification system.
This system runs without needing a user prompt — it thinks and acts like a real digital assistant.

⚙️ Setup & Installation
1. Clone the Repository
git clone https://github.com/Aatka-Saleem/fitness_testing.git
cd fitness_testing
2. Create a Virtual Environment
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Configure Secrets
Create .streamlit/secrets.toml with your Firebase service account:
toml
[firebase]
type = "service_account"
project_id = "<your_project_id>"
...
Create .env file in the project root:
GROQ_API_KEY=your_groq_api_key
FITNESS_UAGENT_ADDRESS=your_agent_wallet_address
5. Run the Application
Open two terminal windows:
Terminal 1 — Run the Autonomous Agent
python run_fetch_agent.py
Terminal 2 — Start the Web App
streamlit run streamlit_app.py

☁️ Deployment on Vultr
This app is designed for deployment on Vultr’s cloud infrastructure. You can deploy both the agent and the frontend as long-running services using:
Streamlit on a Vultr Ubuntu VM or Docker container
Python agent as a background service (e.g., with systemd or Docker)
Firebase remains your cloud-hosted backend

🏁 What's Next
This project can easily be extended for:
Multi-org HR dashboards for admins
SMS or Slack integrations for nudges
Advanced analytics (engagement, goal tracking)
Rewards system for wellness achievements

🧑‍💼 Built For
HR Leaders aiming to boost employee health
Startups fostering a wellness-first culture
Enterprise wellness programs powered by AI
Hackathons showcasing agentic workflows in real-world use cases

👥 Team & Acknowledgments
Built for raise your hackathon for the Vultr x Agentic Workflows Hackathon.
Thanks to Fetch.ai, Groq, Streamlit, and Vultr for making this possible.
Team Leader:
AATKA
TEAM MEMBERS:
AREEBA SHAKEEL
KHOLAH REHAN
NAVEERA SHARIF
SYEDA ANEEQA FATIMA

