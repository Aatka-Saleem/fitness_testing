import streamlit as st
import asyncio

def app():
    st.header("🔐 Welcome to the Enterprise Wellness Agent")
    st.write("Please sign up or log in to continue.")

    if 'backend' not in st.session_state:
        st.error("Backend not initialized.")
        return
    backend = st.session_state.backend

    # --- Load Organizations for the dropdown ---
    if 'organizations' not in st.session_state:
        st.session_state.organizations = asyncio.run(backend.get_all_organizations())
    
    organizations = st.session_state.get('organizations', [])
    if not organizations:
        st.warning("No organizations found. Please ask an admin to create one first.")
        return
    
    org_map = {org['name']: org['id'] for org in organizations}
    
    with st.form("login_form"):
        selected_org_name = st.selectbox("Select Your Organization", options=org_map.keys())
        email = st.text_input("Your Email Address")
        name = st.text_input("Your Name (only needed for first-time sign-up)")
        submitted = st.form_submit_button("Login / Sign Up")

        if submitted:
            if not email or not selected_org_name:
                st.warning("Please provide your email and select an organization.")
            else:
                org_id = org_map[selected_org_name]
                with st.spinner("Checking your credentials..."):
                    # Check if user exists in Firebase Auth
                    user = asyncio.run(backend.get_user_by_email(email))
                    
                    if user:
                        # User exists, log them in and get their profile
                        profile = asyncio.run(backend.get_user_profile(user.uid, org_id))
                        if profile:
                            is_admin = profile.get('is_admin', False)
                            st.success(f"Welcome back, {user.display_name}!")
                            st.session_state.logged_in = True
                            st.session_state.user_info = {'uid': user.uid, 'email': user.email, 'name': user.display_name, 'org_id': org_id, 'is_admin': is_admin}
                            st.rerun()
                        else:
                            st.error("Could not find your profile in this organization.")
                    else:
                        # User does not exist, create a new one
                        if not name:
                            st.warning("Please provide your name to sign up.")
                        else:
                            st.info("Creating a new account for you...")
                            # Check if this will be the first user in the org to make them an admin
                            org_users_ref = backend.db.collection('organizations').document(org_id).collection('users')
                            is_first_user = not org_users_ref.limit(1).get()

                            uid, is_admin = asyncio.run(backend.create_user_in_auth_and_firestore(org_id, name, email, is_admin=is_first_user))
                            
                            if uid:
                                st.success("Account created successfully! Logging you in.")
                                st.session_state.logged_in = True
                                st.session_state.user_info = {'uid': uid, 'email': email, 'name': name, 'org_id': org_id, 'is_admin': is_admin}
                                st.rerun()

