import json
import os
from datetime import datetime
import streamlit as st
import pandas as pd

DATA_FILE = "team_tracker_data.json"

DEFAULT_TEAMS = [
    {'id': 1, 'name': 'Group 1', 'color': 'Blue', 'members': [
        'Sreejith Sreekumar', 'Vishal Anbuselvi Sharavanan', 'Ajesh Raj', 'Sreerag Sasikumar', 'Navya Nair'
    ]},
    {'id': 2, 'name': 'Group 2', 'color': 'Green', 'members': [
        'Emerson Johnson', 'Anagha Rajasree', 'Alfin Joji', 'Joel Ivan', 'Lubina Anwer'
    ]},
    {'id': 3, 'name': 'Group 3', 'color': 'Purple', 'members': [
        'Gokulraj Rajan', 'Desma Davis', 'Rahul Rajendran', 'Arya Sarang'
    ]},
    {'id': 4, 'name': 'Group 4', 'color': 'Orange', 'members': [
        'Geethu Sherly Satheesh', 'Thara Rani', 'Amritha Ramesh', 'Arsha Sajeev'
    ]},
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                teams = data.get('teams', DEFAULT_TEAMS)
                sessions = data.get('sessions', [])
                return teams, sessions
        except Exception as e:
            st.warning(f"Error loading data: {e}")
    return DEFAULT_TEAMS, []

def save_data(teams, sessions):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({'teams': teams, 'sessions': sessions}, f, indent=2)
        st.toast("Data saved", icon="✅")
    except Exception as e:
        st.error(f"Error saving data: {e}")

def calculate_team_scores(teams, sessions):
    scores = {team['id']: 0 for team in teams}
    for session in sessions:
        # Attendance (5 per present member)
        for member, present in session.get('attendance', {}).items():
            if present:
                team = next((t for t in teams if member in t['members']), None)
                if team:
                    scores[team['id']] += 5

        # Presentation
        host_team = next((t for t in teams if t['name'] == session.get('hostTeam')), None)
        if host_team:
            presentation_total = sum(int(v) for v in session.get('presentationScores', {}).values())
            scores[host_team['id']] += presentation_total

        # Games
        for game in session.get('games', []):
            if game.get('winner'):
                if game['type'] == 'team':
                    team_id = int(game['winner'])
                    scores[team_id] += 10
                else:
                    team = next((t for t in teams if game['winner'] in t['members']), None)
                    if team:
                        scores[team['id']] += 5

        # Hosting
        if host_team:
            hosting_total = sum(int(v) for v in session.get('hostingScores', {}).values())
            scores[host_team['id']] += hosting_total
    return scores

def session_table(sessions):
    if not sessions:
        return pd.DataFrame(columns=["id", "date", "hostTeam", "presenter", "attendanceCount", "presentationScore", "hostingScore", "games"])
    rows = []
    for s in sessions:
        rows.append({
            "id": s["id"],
            "date": s["date"],
            "hostTeam": s["hostTeam"],
            "presenter": s["presenter"],
            "attendanceCount": sum(1 for v in s.get("attendance", {}).values() if v),
            "presentationScore": sum(int(v) for v in s.get("presentationScores", {}).values()),
            "hostingScore": sum(int(v) for v in s.get("hostingScores", {}).values()),
            "games": len(s.get("games", [])),
        })
    df = pd.DataFrame(rows).sort_values("date", ascending=False)
    return df

# ============ Streamlit UI ============

st.set_page_config(page_title="Team Building Activity Tracker", page_icon="🏆", layout="wide")
st.title("🏆 Team Building Activity Tracker")

# Load once and keep in session_state for UX
if "teams" not in st.session_state or "sessions" not in st.session_state:
    teams, sessions = load_data()
    st.session_state.teams = teams
    st.session_state.sessions = sessions

teams = st.session_state.teams
sessions = st.session_state.sessions

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Leaderboard", "Sessions", "Add Session", "Score & Attendance", "Data"
])

with tab1:
    st.subheader("Leaderboard")
    scores = calculate_team_scores(teams, sessions)
    leaderboard = sorted(teams, key=lambda t: scores[t['id']], reverse=True)
    
    # Edit Teams Button
    col1, col2 = st.columns([1, 0.2])
    with col2:
        if st.button("✏️ Edit Teams", key="edit_teams_btn"):
            st.session_state.editing_teams = not st.session_state.get('editing_teams', False)
    
    editing_teams = st.session_state.get('editing_teams', False)
    
    cols = st.columns(4)
    for i, team in enumerate(leaderboard):
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"### {i + 1}. {team['name']}  —  **{scores[team['id']]}** pts")
                st.caption(f"Color: {team['color']}")
                st.write("Members:", ", ".join(team['members']))
                
                if editing_teams:
                    # Add member
                    new_member = st.text_input(f"Add member to {team['name']}", key=f"add_member_{team['id']}")
                    if new_member and st.button("Add", key=f"add_btn_{team['id']}"):
                        if new_member not in team['members']:
                            team['members'].append(new_member)
                            st.session_state.teams = teams
                            save_data(teams, sessions)
                            st.rerun()
                    
                    # Remove members
                    st.write("**Remove Members:**")
                    for member in team['members']:
                        col_member, col_remove = st.columns([0.8, 0.2])
                        with col_member:
                            st.write(member)
                        with col_remove:
                            if st.button("🗑️", key=f"remove_{team['id']}_{member}"):
                                team['members'].remove(member)
                                st.session_state.teams = teams
                                save_data(teams, sessions)
                                st.rerun()

with tab2:
    st.subheader("All Sessions")
    df = session_table(sessions)
    st.dataframe(df, use_container_width=True)

with tab3:
    st.subheader("Add New Session")
    with st.form("add_session_form"):
        date = st.date_input("Date", value=datetime.today())
        host_team_name = st.selectbox("Host Team", [t['name'] for t in teams])
        host_team = next((t for t in teams if t['name'] == host_team_name), None)
        if host_team is None:
            st.error("Selected team not found!")
            presenter = None
        else:
            presenter = st.selectbox("Presenter", host_team['members'])
        submitted = st.form_submit_button("Add Session")
        if submitted and host_team is not None:
            new_session = {
                'id': (max([s['id'] for s in sessions]) + 1) if sessions else 1,
                'date': date.strftime("%Y-%m-%d"),
                'hostTeam': host_team['name'],
                'presenter': presenter,
                'attendance': {},
                'presentationScores': {},
                'games': [],
                'hostingScores': {}
            }
            sessions.append(new_session)
            st.session_state.sessions = sessions
            save_data(teams, sessions)
            st.success(f"Session added for {new_session['date']} (Host: {host_team_name})")
            st.rerun()

with tab4:
    st.subheader("Record Attendance / Scores / Games")
    if not sessions:
        st.info("No sessions yet. Add one in the 'Add Session' tab.")
    else:
        which = st.selectbox("Select Session", [f"#{s['id']} • {s['date']} • {s['hostTeam']}" for s in sessions])
        session_id = int(which.split('•')[0].strip().replace('#', ''))
        session = next((s for s in sessions if s['id'] == session_id), None)
        
        if session is None:
            st.error("Selected session not found!")
        else:
            colA, colB = st.columns(2, gap="large")

            # Attendance
            with colA:
                st.markdown("### Attendance")
                all_members = [m for t in teams for m in t['members']]
                for member in all_members:
                    default = session.get('attendance', {}).get(member, False)
                    present = st.checkbox(member, value=default, key=f"att_{session_id}_{member}")
                    session.setdefault('attendance', {})[member] = present
                if st.button("Save Attendance"):
                    save_data(teams, sessions)

            # Presentation & Hosting scores
            with colB:
                st.markdown(f"### Scores (Host: {session['hostTeam']})")
                
                # Presentation - other teams rate host
                st.write("**Presentation Scores (0–5 from other teams)**")
                for team in teams:
                    if team['name'] != session['hostTeam']:
                        val = session.get('presentationScores', {}).get(str(team['id']), session.get('presentationScores', {}).get(team['id'], 0))
                        score = st.number_input(
                            f"Score from {team['name']}",
                            min_value=0, max_value=5, step=1, value=int(val) if isinstance(val, int) else int(val or 0),
                            key=f"pres_{session_id}_{team['id']}"
                        )
                        session.setdefault('presentationScores', {})[str(team['id'])] = int(score)
                st.caption(f"Total presentation score: {sum([int(v) for v in session.get('presentationScores', {}).values()])}/15")

                st.write("**Hosting Scores (0–5 from other teams)**")
                for team in teams:
                    if team['name'] != session['hostTeam']:
                        val = session.get('hostingScores', {}).get(str(team['id']), session.get('hostingScores', {}).get(team['id'], 0))
                        score = st.number_input(
                            f"Hosting score from {team['name']}",
                            min_value=0, max_value=5, step=1, value=int(val) if isinstance(val, int) else int(val or 0),
                            key=f"host_{session_id}_{team['id']}"
                        )
                        session.setdefault('hostingScores', {})[str(team['id'])] = int(score)
                st.caption(f"Total hosting score: {sum([int(v) for v in session.get('hostingScores', {}).values()])}/15")

            # Games Section
            st.markdown("### Games")
            if 'games' not in session:
                session['games'] = []
            
            with st.form(f"add_game_{session_id}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    game_name = st.text_input("Game name")
                with col2:
                    game_type = st.selectbox("Game type", ["team", "individual"])
                with col3:
                    if game_type == "team":
                        winner_team = st.selectbox("Winning Team", [f"{t['id']} - {t['name']}" for t in teams])
                        winner_value = winner_team.split(" - ")[0]
                    else:
                        all_members = [m for t in teams for m in t['members']]
                        winner_value = st.selectbox("Winner (Member)", all_members)
                
                add_game = st.form_submit_button("Add Game")
                if add_game and game_name and winner_value:
                    game = {
                        'id': (max([g['id'] for g in session['games']]) + 1) if session['games'] else 1,
                        'name': game_name,
                        'type': game_type,
                        'winner': winner_value
                    }
                    session['games'].append(game)
                    save_data(teams, sessions)
                    st.success("Game added")
                    st.rerun()

            # Display existing games
            if session['games']:
                st.write("**Existing Games:**")
                games_df = pd.DataFrame(session['games'])
                st.table(games_df)
                
                # Delete game buttons
                for game in session['games']:
                    if st.button(f"Delete game: {game['name']}", key=f"delete_game_{game['id']}"):
                        session['games'] = [g for g in session['games'] if g['id'] != game['id']]
                        save_data(teams, sessions)
                        st.rerun()

            # Save button
            if st.button("Save Scores & Games"):
                save_data(teams, sessions)
                st.success("All changes saved!")

with tab5:
    st.subheader("Data Export / Import")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Export Current Data**")
        export_obj = {'teams': teams, 'sessions': sessions}
        st.download_button(
            label="Download JSON",
            file_name="team_tracker_export.json",
            mime="application/json",
            data=json.dumps(export_obj, indent=2)
        )
    
    with col2:
        st.write("**Import Data**")
        up = st.file_uploader("Upload a JSON export", type=["json"])
        if up is not None:
            try:
                data = json.load(up)
                st.session_state.teams = data.get('teams', teams)
                st.session_state.sessions = data.get('sessions', sessions)
                save_data(st.session_state.teams, st.session_state.sessions)
                st.success("Imported data and saved to file.")
                st.rerun()
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
    
    st.caption("💡 Tip: For multi-user/long-term persistence, connect a hosted DB (e.g., Supabase Postgres).")
    
    # Delete session option
    st.write("**Delete Session**")
    if sessions:
        session_to_delete = st.selectbox("Select session to delete", 
                                        [f"#{s['id']} • {s['date']} • {s['hostTeam']}" for s in sessions],
                                        key="delete_session_select")
        if session_to_delete:
            session_id = int(session_to_delete.split('•')[0].strip().replace('#', ''))
            if st.button("🗑️ Delete This Session", key="delete_session_btn"):
                sessions = [s for s in sessions if s['id'] != session_id]
                st.session_state.sessions = sessions
                save_data(teams, sessions)
                st.success("Session deleted!")
                st.rerun()
