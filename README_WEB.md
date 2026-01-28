# Team Building Activity Tracker - Web Version

A Flask-based web application for tracking team building activities with a modern, interactive UI.

## Installation

```bash
pip install -r requirements_web.txt
```

## Running the Application

```bash
python app_web.py
```

The application will be available at `http://localhost:5000`

## Features

- **Leaderboard**: Real-time team scoring with color-coded rankings
- **Session Management**: Create and manage team building sessions
- **Attendance Tracking**: Mark team members as present (5 points each)
- **Presentation Scoring**: Score presentations from other teams (0-5 points, max 15)
- **Game Results**: Track team and individual game wins (10 and 5 points respectively)
- **Hosting Scores**: Rate the hosting team's performance (0-5 points, max 15)
- **Team Management**: Add and remove team members dynamically
- **Data Persistence**: All data is automatically saved to `team_tracker_web.json`

## Data Structure

The application stores data in JSON format with:
- Teams with their members and colors
- Sessions with dates, attendance, presentation scores, hosting scores, and game results
- Automatic score calculation based on all activities

## Scoring System

- Attendance: 5 points per present member
- Presentation: 0-5 points from each of the 3 non-hosting teams (max 15)
- Games: 10 points for team game wins, 5 points for individual wins
- Hosting: 0-5 points from each of the 3 non-hosting teams (max 15)
