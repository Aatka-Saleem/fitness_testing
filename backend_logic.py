import os
import streamlit as st
from dotenv import load_dotenv
from groq import AsyncGroq
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime, timedelta
import asyncio

# Load local .env environment variables for local development
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Cached Firestore client loader (runs once per session) ---
@st.cache_resource
def get_firestore_client():
    """Initializes and returns the Firestore client and auth service."""
    try:
        if not firebase_admin._apps:
            if "firebase_config" in st.secrets:
                creds = credentials.Certificate(dict(st.secrets["firebase_config"]))
                firebase_admin.initialize_app(creds)
            else:
                st.error("Firebase config not found in st.secrets.")
                return None, None
        return firestore.client(), auth
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        return None, None

class Backend:
    """
    Manages all backend logic: Firebase, Groq AI, and fitness calculations.
    """
    def __init__(self):
        if "backend_initialized" not in st.session_state:
            self.db, self.auth = get_firestore_client()
            st.session_state.db = self.db
            st.session_state.auth = self.auth

            if not GROQ_API_KEY:
                st.error("GROQ_API_KEY not found.")
                st.session_state.groq_client = None
            else:
                st.session_state.groq_client = AsyncGroq(api_key=GROQ_API_KEY)
            
            st.session_state.backend_initialized = True
        
        self.db = st.session_state.db
        self.auth = st.session_state.auth
        self.groq_client = st.session_state.groq_client

    # --- AI Method ---
    async def get_ai_response(self, system_prompt, user_prompt, model="llama3-8b-8192", max_tokens=2000, temperature=0.7):
        if not self.groq_client:
            return "AI service is unavailable."
        
        full_response = ""
        try:
            stream = await self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=model, max_tokens=max_tokens, temperature=temperature, stream=True
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            return full_response.strip()
        except Exception as e:
            st.error(f"Error with AI API: {e}")
            return "An error occurred with the AI service."

    # --- Organization & Team Methods ---
    async def create_organization(self, org_name: str, created_by_uid: str) -> str | None:
        if not self.db: return None
        try:
            org_ref = self.db.collection('organizations').document()
            org_ref.set({'name': org_name, 'created_at': firestore.SERVER_TIMESTAMP, 'created_by': created_by_uid})
            return org_ref.id
        except Exception as e:
            st.error(f"Error creating organization: {e}"); return None

    async def get_all_organizations(self) -> list:
        if not self.db: return []
        try:
            docs = self.db.collection('organizations').stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            st.error(f"Error getting organizations: {e}"); return []

    async def add_team_to_organization(self, org_id: str, team_name: str) -> bool:
        if not self.db: return False
        try:
            self.db.collection('organizations').document(org_id).collection('teams').add({'name': team_name, 'created_at': firestore.SERVER_TIMESTAMP})
            return True
        except Exception as e:
            st.error(f"Error adding team: {e}"); return False
            
    def get_teams_for_organization(self, org_id: str) -> list:
        """Synchronous method to get teams, easier to call inside loops in Streamlit."""
        if not self.db: return []
        try:
            teams_ref = self.db.collection("organizations").document(org_id).collection("teams")
            return [doc.to_dict() | {'id': doc.id} for doc in teams_ref.stream()]
        except Exception as e:
            st.error(f"Error getting teams: {e}"); return []

    async def rename_team(self, org_id: str, team_id: str, new_name: str) -> bool:
        if not self.db: return False
        try:
            self.db.collection("organizations").document(org_id).collection("teams").document(team_id).update({"name": new_name})
            return True
        except Exception as e:
            st.error(f"Error renaming team: {e}"); return False

    async def delete_team(self, org_id: str, team_id: str) -> bool:
        if not self.db: return False
        try:
            self.db.collection("organizations").document(org_id).collection("teams").document(team_id).delete()
            return True
        except Exception as e:
            st.error(f"Error deleting team: {e}"); return False

    # --- User Management Methods ---
    async def get_user_by_email(self, email: str):
        if not self.auth: return None
        try:
            return self.auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            st.error(f"Error getting user by email: {e}"); return None

    async def create_user_in_auth_and_firestore(self, org_id: str, name: str, email: str, is_admin: bool = False) -> tuple[str | None, bool]:
        if not self.auth or not self.db: return None, False
        try:
            new_user = self.auth.create_user(email=email, display_name=name)
            uid = new_user.uid
            profile_data = {
                'uid': uid, 'org_id': org_id, 'name': name, 'email': email, 'is_admin': is_admin,
                'created_at': firestore.SERVER_TIMESTAMP,
                'body_metrics': {'weight_kg': 70, 'height_cm': 175, 'age': 30, 'gender': 'Male'}
            }
            await self.update_user_profile(uid, org_id, profile_data)
            return uid, is_admin
        except Exception as e:
            st.error(f"Error creating new user: {e}"); return None, False

    async def get_user_profile(self, user_uid: str, org_id: str) -> dict | None:
        if not self.db: return None
        try:
            user_ref = self.db.collection('organizations').document(org_id).collection('users').document(user_uid)
            user_doc = user_ref.get()
            if user_doc.exists:
                return user_doc.to_dict()
            else:
                st.info("Creating a default profile for you in this organization...")
                user_auth_record = self.auth.get_user(user_uid)
                default_profile = {
                    'uid': user_uid, 'org_id': org_id, 'name': user_auth_record.display_name or "New User",
                    'email': user_auth_record.email, 'is_admin': False,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'body_metrics': {'weight_kg': 70, 'height_cm': 175, 'age': 30, 'gender': 'Male'}
                }
                await self.update_user_profile(user_uid, org_id, default_profile)
                return default_profile
        except Exception as e:
            st.error(f"Error getting user profile: {e}"); return None

    async def update_user_profile(self, user_uid: str, org_id: str, data: dict) -> bool:
        if not self.db: return False
        try:
            user_ref = self.db.collection('organizations').document(org_id).collection('users').document(user_uid)
            user_ref.set(data, merge=True)
            return True
        except Exception as e:
            st.error(f"Error updating user profile: {e}"); return False

    # --- Fitness Data Methods ---
    async def save_daily_log(self, user_uid: str, org_id: str, log_data: dict) -> bool:
        if not self.db: return False
        try:
            log_date = log_data.get('date')
            if hasattr(log_date, 'to_pydatetime'):
                log_date = log_date.to_pydatetime()
            
            date_str = log_date.strftime('%Y-%m-%d')
            log_data['date'] = log_date

            log_ref = self.db.collection('organizations').document(org_id).collection('users').document(user_uid).collection('daily_logs').document(date_str)
            log_ref.set(log_data)
            return True
        except Exception as e:
            st.error(f"Error saving daily log: {e}"); return False

    async def get_daily_logs(self, org_id: str, user_uid: str) -> list:
        if not self.db: return []
        try:
            logs_ref = self.db.collection('organizations').document(org_id).collection('users').document(user_uid).collection('daily_logs')
            docs = logs_ref.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            st.error(f"Error getting daily logs: {e}"); return []

    async def save_notification(self, org_id: str, user_uid: str, message: str) -> bool:
        if not self.db: return False
        try:
            ref = self.db.collection('organizations').document(org_id).collection('users').document(user_uid).collection('notifications').document()
            ref.set({'message': message, 'timestamp': firestore.SERVER_TIMESTAMP, 'read': False})
            return True
        except Exception as e:
            st.error(f"Error saving notification: {e}"); return False
            
    async def get_notifications(self, org_id: str, user_uid: str) -> list:
        """Retrieves all unread notifications for a user."""
        if not self.db: return []
        try:
            ref = self.db.collection('organizations').document(org_id).collection('users').document(user_uid).collection('notifications')
            query = ref.where('read', '==', False)
            docs = query.stream()
            # --- FIX: Include the document ID with the data ---
            return [doc.to_dict() | {'id': doc.id} for doc in docs]
        except Exception as e:
            st.error(f"Error getting notifications: {e}"); return []
            
    async def mark_notification_as_read(self, org_id: str, user_uid: str, notification_id: str) -> bool:
        if not self.db: return False
        try:
            ref = self.db.collection('organizations').document(org_id).collection('users').document(user_uid).collection('notifications').document(notification_id)
            ref.update({'read': True})
            return True
        except Exception as e:
            st.error(f"Error updating notification: {e}"); return False
    
    # In backend_logic.py, add this function inside the Backend class

    async def rename_organization(self, org_id: str, new_name: str) -> bool:
        """Renames an existing organization."""
        if not self.db: return False
        try:
            self.db.collection("organizations").document(org_id).update({"name": new_name})
            return True
        except Exception as e:
            st.error(f"Error renaming organization: {e}"); return False

    # --- Calculation & Utility Methods ---
    def get_todays_tip(self):
        tips = ["Stay hydrated!", "Rest is crucial for muscle growth.", "Consistency beats intensity."]
        return tips[datetime.now().day % len(tips)]

    def calculate_bmi(self, weight_kg, height_cm):
        if height_cm > 0: return round(weight_kg / ((height_cm / 100) ** 2), 2)
        return 0.0

    def calculate_body_fat(self, bmi, age, gender):
        if gender == "Male": return round((1.20 * bmi) + (0.23 * age) - 16.2, 1)
        return round((1.20 * bmi) + (0.23 * age) - 5.4, 1)

    def calculate_bmr(self, weight_kg, height_cm, age, gender):
        if gender == "Male": return int(10 * weight_kg + 6.25 * height_cm - 5 * age + 5)
        return int(10 * weight_kg + 6.25 * height_cm - 5 * age - 161)
