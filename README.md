AI Training Module Generator – Backend
Overview

This backend application converts recurring meeting notes into structured training modules.
It stores meeting notes, processes them using AI, and exposes APIs that the frontend uses to display generated topics and training content.

What This Backend Does

Accepts meeting notes (text or file content)

Stores notes in the database

Groups similar discussions

Uses AI to generate training content

Tracks versions of generated modules

Exposes APIs for frontend consumption

Tech Stack

Python

Django

Django REST Framework

SQLite (for development)

Google Gemini API (content generation)

Project Structure (Simplified)
meeting_training/
 ├─ trainer/
 │   ├─ models.py        # Database models
 │   ├─ views.py         # API endpoints
 │   ├─ serializers.py  # Request/response handling
 │   ├─ utility.py      # AI processing logic
 │   ├─ urls.py         # API routes
 ├─ output/              # Generated training content (ignored in git)
 ├─ manage.py
 ├─ requirements.txt
 └─ .env                 # API keys (ignored)

APIs Provided
API	Purpose
POST /api/transcripts/	Upload meeting notes
POST /api/process-ai/	Trigger AI processing
GET /api/topics/	Fetch generated topics
GET /api/module/{topic}	Fetch training module content
Environment Setup
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-training-backend.git
cd ai-training-backend

2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3. Install dependencies
pip install -r requirements.txt

4. Create .env file
GEMINI_API_KEY=your_api_key_here


⚠️ Do not commit this file.

5. Run migrations
python manage.py migrate

6. Start server
python manage.py runserver


Backend runs at:

http://127.0.0.1:8000

Notes

AI output is generated on demand

No model training is done locally

This backend is designed for internal knowledge sharing

Use Cases

Team onboarding

Internal training documentation

Knowledge reuse from meetings

Reducing repeated explanations

License

Internal / Educational use
