# Smart Scheduler v2

AI-Powered Meeting Notes Analysis and Schedule Management System

[한국어](./README.md)

## Overview

Smart Scheduler v2 is a web-based schedule management system that automatically analyzes meeting notes using Google Gemini AI and registers extracted information to an integrated calendar. It automatically extracts tasks, schedules, and key information from meeting notes to support efficient work management.

## Key Features

### AI-Powered Automatic Analysis
- Meeting notes analysis using Google Gemini 2.5 Flash model
- Automatic extraction of meeting summaries, tasks, schedules, participants, and decisions
- Automatic conversion of relative date expressions ("end of January" → `2026-01-31`)
- Automatic department name recognition and prefix addition to task/schedule titles

### Integrated Calendar Management
- Intuitive schedule management interface based on FullCalendar
- Unified management of Summaries, Tasks, and Meetings
- Color-coded event types (Summary: blue, Task: yellow, Meeting: green)
- Drag-and-drop schedule adjustment

### Context Linking System
- Automatic linking between tasks/schedules and original meeting notes
- Instant access to related meeting notes when clicking events
- Manual context link configuration

### Advanced Editing Features
- Markdown editing based on Toast UI Editor
- Fullscreen editor mode support
- Real-time preview

### Data Management
- JSON-based local database
- Automatic backup generation (with timestamps)
- Event CRUD operations support

## System Requirements

- Python 3.8 or higher
- Docker and Docker Compose (optional)
- Google Gemini API key
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation and Execution

### 1. Clone Repository

```bash
git clone https://github.com/chaninjung/meeting-notes-automation.git
cd meeting-notes-automation
```

### 2. Environment Configuration

Create a `.env` file and enter the following:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

**How to obtain Gemini API key:**
1. Visit https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 3. Execution Methods

#### Using Docker (Recommended)

```bash
docker compose up -d
```

#### Direct Python Execution

```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) Start with example data
cp data/db.example.json data/db.json

# Run server
python app.py
```

### 4. Access

Open http://localhost:5000 in your web browser

## Usage

### Meeting Notes Analysis

1. **Input Notes**: Enter meeting notes text in the "Meeting Notes" area on the left panel
2. **Run Analysis**: Click the "Analyze Notes" button
3. **Review Results**: Check and modify analysis results in the Staging Area
4. **Register to Calendar**: Click "Add to Calendar" button to register events

### Utilizing Staging Area

Analysis results are categorized into three types:

- **Meeting Summary**: Meeting overview (title, date, content editable)
- **Tasks**: To-do items (title, date, time, priority adjustable)
- **Meetings**: Scheduled events (title, date, time configurable)

Each item can be selected/deselected via checkbox to determine calendar registration.

### Event Management

- **View**: Click event on calendar
- **Edit**: Click "Edit Event" in event detail modal
- **Delete**: Click "Delete Event" in edit modal
- **Link Context**: Select related meeting notes from "Linked Context" dropdown in edit modal

## Meeting Notes Writing Guide

Recommended format for improved analysis accuracy:

```markdown
# Meeting Notes - [Department Name]

**Date:** YYYY-MM-DD
**Time:** HH:MM - HH:MM
**Participants:** [Participant list]

## Discussion Items

1. **[Topic 1]**
   - Details
   - Deadline: [Date]
   - Assignee: [Name]

2. **[Topic 2]**
   - Details

## Decisions

- [Decision 1]
- [Decision 2]

## Next Meeting

- Date: [Date]
- Time: [Time]
```

## API Documentation

### POST /analyze

Analyzes meeting notes text.

**Request Body:**
```json
{
  "text": "Meeting notes content..."
}
```

**Response:**
```json
{
  "meeting_title": "Topic/Department/YY-MM-DD",
  "meeting_date": "YYYY-MM-DD",
  "department_name": "Department Name",
  "summary": "Markdown formatted summary",
  "todo_tasks": [...],
  "schedule_items": [...]
}
```

### GET /events

Retrieves all saved events.

### POST /events

Creates a new event.

### PUT /events/<id>

Updates a specific event.

### DELETE /events/<id>

Deletes a specific event.

## Project Structure

```
meeting-notes-automation/
├── .env                    # Environment variables
├── app.py                  # Flask backend server
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── data/
│   ├── db.json            # Event database
│   └── backups/           # Automatic backups
├── src/
│   └── gemini_analyzer.py # Gemini AI analysis module
└── templates/
    └── index.html         # Frontend UI
```

## Technology Stack

### Backend
- Python 3.8+
- Flask 3.0.0
- Google Generative AI (Gemini 2.5 Flash)

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Tailwind CSS 3.x
- FullCalendar 6.1.10
- Toast UI Editor
- Marked.js (Markdown parsing)

## Cost Information

This system is available for free:

- **Gemini API**: Free tier (1,500 requests per day)
- **Server**: Local execution (no separate server costs)

In typical usage environments, analyzing 10-20 meeting notes per day is possible within the free quota.

## Troubleshooting

### API Key Error

```
Error: GEMINI_API_KEY is not configured.
```

**Solution**: Verify that the correct API key is entered in the `.env` file

### Dependency Error

```
ModuleNotFoundError: No module named 'google.generativeai'
```

**Solution**:
```bash
pip install -r requirements.txt
```

### Port Conflict

```
Error: Address already in use
```

**Solution**:
```bash
PORT=8080 python app.py
```

## License

MIT License

Copyright (c) 2026

This software is distributed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contributing

Bug reports and feature suggestions can be submitted through [Issues](https://github.com/chaninjung/meeting-notes-automation/issues).

Pull Requests are always welcome.

## Contact

For project-related inquiries, please use the Issues tab.

## Developer

**nini** - Initial work and development

---

**Powered by Google Gemini AI**
