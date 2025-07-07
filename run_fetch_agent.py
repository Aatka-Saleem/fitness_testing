import asyncio
from datetime import datetime, timedelta
import pytz
from uagents import Agent, Context

# Import the backend class to interact with the database
from backend_logic import Backend

# --- Agent Configuration ---
AGENT_NAME = "autonomous_wellness_agent"
AGENT_SEED = "a_very_secret_seed_for_the_autonomous_agent" # Change this
CHECK_INTERVAL_SECONDS = 3600.0 # Check once per hour

# Create the agent
agent = Agent(name=AGENT_NAME, seed=AGENT_SEED)

# Initialize our application's backend
backend = Backend()

async def generate_nudge(user_profile: dict) -> str:
    """Helper function to generate the AI nudge."""
    system_prompt = f"""
    You are an empathetic and motivating AI wellness coach.
    A user, {user_profile.get('name', 'User')}, has not logged a workout in a few days.
    Their goal is: {user_profile.get('body_metrics', {}).get('fitness_goal', 'not set')}.
    Your task is to provide a short (2-3 sentences), positive, and actionable piece of advice to encourage them.
    Address them by their name.
    """
    user_prompt = "Give me a personalized motivational nudge to get back on track."
    return await backend.get_ai_response(system_prompt, user_prompt)

@agent.on_interval(period=CHECK_INTERVAL_SECONDS)
async def check_for_inactive_users(ctx: Context):
    """
    This is the main function of the agent. It runs on a schedule,
    finds inactive users, and sends them a motivational nudge.
    """
    ctx.logger.info(f"Agent running check at {datetime.now()}...")
    if not backend.db:
        ctx.logger.error("Database not initialized. Agent cannot run."); return

    organizations = await backend.get_all_organizations()
    if not organizations:
        ctx.logger.info("No organizations found."); return

    for org in organizations:
        org_id = org['id']
        org_name = org.get('name', 'Unnamed Org')
        ctx.logger.info(f"Checking organization: {org_name}")
        try:
            users_ref = backend.db.collection('organizations').document(org_id).collection('users')
            all_users_in_org = [doc.to_dict() for doc in users_ref.stream()]

            for user_profile in all_users_in_org:
                user_uid = user_profile.get("uid")
                user_name = user_profile.get("name", "User")
                if not user_uid: continue

                daily_logs = await backend.get_daily_logs(org_id, user_uid)
                
                has_worked_out_recently = False
                if daily_logs:
                    three_days_ago = datetime.now(pytz.utc) - timedelta(days=3)
                    for log in daily_logs:
                        log_date = log.get('date')
                        if isinstance(log_date, datetime):
                            if log_date.tzinfo is None:
                                log_date = pytz.utc.localize(log_date)
                            
                            if log_date > three_days_ago and log.get("workout_duration_min", 0) > 0:
                                has_worked_out_recently = True
                                break
                
                if not has_worked_out_recently:
                    ctx.logger.info(f"User {user_name} is inactive. Generating nudge.")
                    nudge_message = await generate_nudge(user_profile)
                    await backend.save_notification(org_id, user_uid, nudge_message)
                    ctx.logger.info(f"Successfully sent nudge to {user_name}.")
                else:
                    ctx.logger.info(f"User {user_name} is active. No nudge needed.")
        except Exception as e:
            ctx.logger.error(f"Failed to process organization {org_name}: {e}")

if __name__ == "__main__":
    print(f"Starting agent '{AGENT_NAME}'. Press Ctrl+C to exit.")
    agent.run()
