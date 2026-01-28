from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "team_tracker_web.json"

DEFAULT_DATA = {
    "teams": [
        {"id": 1, "name": "Group 1", "color": "bg-blue-500", "members": ["Sreejith Sreekumar", "Vishal Anbuselvi Sharavanan", "Ajesh Raj", "Sreerag Sasikumar", "Navya Nair"]},
        {"id": 2, "name": "Group 2", "color": "bg-green-500", "members": ["Emerson Johnson", "Anagha Rajasree", "Alfin Joji", "Joel Ivan", "Lubina Anwer"]},
        {"id": 3, "name": "Group 3", "color": "bg-purple-500", "members": ["Gokulraj Rajan", "Desma Davis", "Rahul Rajendran", "Arya Sarang"]},
        {"id": 4, "name": "Group 4", "color": "bg-orange-500", "members": ["Geethu Sherly Satheesh", "Thara Rani", "Amritha Ramesh", "Arsha Sajeev"]}
    ],
    "sessions": []
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_team_scores(data):
    scores = {team['id']: 0 for team in data['teams']}
    
    for session in data['sessions']:
        # Attendance (5 points per present member)
        for member, present in session.get('attendance', {}).items():
            if present:
                team = next((t for t in data['teams'] if member in t['members']), None)
                if team:
                    scores[team['id']] += 5
        
        # Presentations
        host_team = next((t for t in data['teams'] if t['name'] == session.get('hostTeam')), None)
        if host_team and session.get('presentationScores'):
            total = sum(int(v) for v in session['presentationScores'].values())
            scores[host_team['id']] += total
        
        # Games
        for game in session.get('games', []):
            if game.get('winner'):
                if game['type'] == 'team':
                    team_id = int(game['winner'])
                    scores[team_id] += 10
                else:
                    team = next((t for t in data['teams'] if game['winner'] in t['members']), None)
                    if team:
                        scores[team['id']] += 5
        
        # Hosting
        if host_team and session.get('hostingScores'):
            total = sum(int(v) for v in session['hostingScores'].values())
            scores[host_team['id']] += total
    
    return scores

@app.route('/')
def index():
    data = load_data()
    scores = calculate_team_scores(data)
    sorted_teams = sorted(data['teams'], key=lambda t: scores[t['id']], reverse=True)
    
    return render_template('index.html', 
                         teams=data['teams'],
                         sorted_teams=sorted_teams,
                         sessions=sorted(data['sessions'], key=lambda s: s['date'], reverse=True),
                         scores=scores)

@app.route('/api/teams', methods=['GET'])
def get_teams():
    data = load_data()
    return jsonify(data['teams'])

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    data = load_data()
    return jsonify(data['sessions'])

@app.route('/api/sessions', methods=['POST'])
def create_session():
    data = load_data()
    session = request.json
    session['id'] = int(datetime.now().timestamp() * 1000)
    session['attendance'] = session.get('attendance', {})
    session['presentationScores'] = session.get('presentationScores', {})
    session['hostingScores'] = session.get('hostingScores', {})
    session['games'] = session.get('games', [])
    
    data['sessions'].append(session)
    save_data(data)
    return jsonify(session), 201

@app.route('/api/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    data = load_data()
    session = next((s for s in data['sessions'] if s['id'] == session_id), None)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    updates = request.json
    session.update(updates)
    save_data(data)
    return jsonify(session)

@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    data = load_data()
    data['sessions'] = [s for s in data['sessions'] if s['id'] != session_id]
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/teams', methods=['PUT'])
def update_teams():
    data = load_data()
    data['teams'] = request.json
    save_data(data)
    return jsonify(data['teams'])

@app.route('/api/scores', methods=['GET'])
def get_scores():
    data = load_data()
    scores = calculate_team_scores(data)
    return jsonify(scores)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
