import asyncio

def get_nudge_from_agent(user_input: str, user_profile: dict, backend) -> str:
    """
    Constructs a prompt and calls the backend's AI function to get a clean nudge message.
    """
    if not user_input:
        return "Please tell me how you're feeling first."

    # Create a detailed prompt for the AI using the user's profile
    system_prompt = f"""
    You are an empathetic and motivating AI wellness coach. The user needs a motivational nudge.

    User's Profile:
    - Name: {user_profile.get('name', 'User')}
    - Stated Goal: {user_profile.get('body_metrics', {}).get('fitness_goal', 'not set')}

    User's current state: "{user_input}"

    Your task is to provide a short (2-3 sentence), positive, and actionable piece of advice or motivation.
    Be encouraging and focus on a small, achievable action. Address the user by their name.
    """

    user_prompt = "Give me only a short 2-3 sentence motivational message. Don't add introductions or labels. Address me by my name and suggest one actionable step."

    response = asyncio.run(backend.get_ai_response(system_prompt, user_prompt))
    return response.strip()
