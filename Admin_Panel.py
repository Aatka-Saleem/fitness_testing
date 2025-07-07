import streamlit as st
import asyncio

def app():
    st.header("🏢 Enterprise Admin Panel")
    st.write("Manage organizations and teams for your Wellness Agent.")

    if 'backend' not in st.session_state or not st.session_state.get('user_info', {}).get('is_admin'):
        st.error("You do not have permission to view this page.")
        return
    backend = st.session_state.backend

    # --- Load existing organizations at the top of the page ---
    if 'organizations' not in st.session_state:
        with st.spinner("Loading organizations..."):
            st.session_state.organizations = asyncio.run(backend.get_all_organizations())
    
    organizations = st.session_state.get('organizations', [])
    org_map = {org.get('name', 'Unnamed'): org['id'] for org in organizations if org.get('id')}

    # --- UI for Creating Orgs and Teams ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Create New Organization")
        with st.form("create_org_form"):
            new_org_name = st.text_input("New Organization Name")
            submitted = st.form_submit_button("✨ Create Organization")
            if submitted and new_org_name:
                admin_uid = st.session_state.user_info['uid']
                with st.spinner(f"Creating '{new_org_name}'..."):
                    org_id = asyncio.run(backend.create_organization(new_org_name, admin_uid))
                    if org_id:
                        st.success(f"Successfully created organization!")
                        st.session_state.pop('organizations', None) # Force reload
                        st.rerun()
                    else:
                        st.error("Failed to create organization.")

    with col2:
        st.subheader("Create New Team")
        if not org_map:
            st.info("Create an organization first.")
        else:
            with st.form("create_team_form"):
                selected_org_name = st.selectbox("Select Organization", options=list(org_map.keys()))
                new_team_name = st.text_input("New Team Name")
                submitted = st.form_submit_button("➕ Add Team")
                if submitted and selected_org_name and new_team_name:
                    selected_org_id = org_map[selected_org_name]
                    with st.spinner(f"Adding team..."):
                        success = asyncio.run(backend.add_team_to_organization(selected_org_id, new_team_name))
                        if success:
                            st.success("Team added successfully!")
                        else:
                            st.error("Failed to add team.")

    # --- Display and Manage Existing Organizations and Teams ---
    st.markdown("---")
    st.subheader("Manage Existing Organizations")
    if not organizations:
        st.info("No organizations created yet.")
    else:
        for org in organizations:
            org_id = org['id']
            org_name = org.get('name', 'Unnamed Org')
            
            with st.expander(f"**{org_name}** (ID: `{org_id}`)", expanded=True):
                
                # --- NEW: Rename Organization Feature ---
                rename_col, teams_col = st.columns([1, 2])
                with rename_col:
                    if st.button("Rename Org", key=f"rename_org_btn_{org_id}"):
                        st.session_state[f'rename_org_mode_{org_id}'] = True
                
                if st.session_state.get(f'rename_org_mode_{org_id}'):
                    with st.form(f"rename_org_form_{org_id}"):
                        new_org_name_input = st.text_input("New Organization Name", value=org_name)
                        submitted = st.form_submit_button("Save Name")
                        if submitted:
                            with st.spinner("Renaming..."):
                                success = asyncio.run(backend.rename_organization(org_id, new_org_name_input))
                                if success:
                                    st.success("Renamed successfully!")
                                    st.session_state.pop(f'rename_org_mode_{org_id}', None)
                                    st.session_state.pop('organizations', None)
                                    st.rerun()
                                else:
                                    st.error("Rename failed.")
                
                st.write("**Teams in this organization:**")
                teams = backend.get_teams_for_organization(org_id)
                if not teams:
                    st.caption("No teams found.")
                else:
                    for team in teams:
                        team_name = team.get("name", "Unnamed Team")
                        team_id = team.get("id", "")
                        
                        t_col1, t_col2, t_col3 = st.columns([3, 1, 1])
                        t_col1.write(f"- {team_name}")
                        
                        if t_col2.button("Rename Team", key=f"rename_team_btn_{team_id}"):
                            st.session_state[f'rename_team_mode_{team_id}'] = True
                        
                        if t_col3.button("Delete Team", key=f"delete_team_btn_{team_id}", type="primary"):
                             with st.spinner("Deleting..."):
                                success = asyncio.run(backend.delete_team(org_id, team_id))
                                if success:
                                    st.success(f"Deleted {team_name}")
                                    st.rerun()
                                else:
                                    st.error("Delete failed.")

                        if st.session_state.get(f'rename_team_mode_{team_id}'):
                            with st.form(f"rename_team_form_{team_id}"):
                                new_name_input = st.text_input("New Team Name", value=team_name)
                                submitted = st.form_submit_button("Save")
                                if submitted:
                                    with st.spinner("Renaming..."):
                                        success = asyncio.run(backend.rename_team(org_id, team_id, new_name_input))
                                        if success:
                                            st.success("Renamed successfully!")
                                            st.session_state.pop(f'rename_team_mode_{team_id}', None)
                                            st.rerun()
                                        else:
                                            st.error("Rename failed.")