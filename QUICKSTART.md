# SmartKoach Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

## Setup in 3 Steps

### 1. Configure API Key

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Replace YOUR_OPENAI_API_KEY with your actual key
```

### 2. Build and Run

```bash
# Build and start both services
docker compose build
docker compose up
```

This will:
- Build the FastAPI backend (port 8000)
- Build the Angular frontend (port 4200)
- Start both services

### 3. Access the Application

Open your browser and navigate to:

```
http://localhost:4200
```

## Usage

1. **Select Domain**: Choose from DSA, ML, DBMS, or OS
2. **Select Difficulty**: Choose Easy, Medium, or Hard
3. **Start Chatting**: Type your message and press Send or Enter
4. **Get Feedback**: The AI will ask questions and provide feedback

## Example Conversation

```
You: "Give me a medium-level DSA question"

SmartKoach: "Here's a question: Given an array of integers, 
find two numbers that add up to a specific target..."

You: "I would use a hash map approach..."

SmartKoach: "Excellent! That's the optimal solution..."
```

## Stopping the Application

```bash
# Stop the services
docker compose down
```

## Troubleshooting

### Backend not starting
- Check that `.env` file exists and contains a valid `OPENAI_API_KEY`
- View logs: `docker compose logs backend`

### Frontend not loading
- Make sure backend is running first
- View logs: `docker compose logs frontend`

### Port already in use
```bash
# Check what's using the ports
lsof -i :4200
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

## Development

### Run backend locally (without Docker)

```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
uvicorn main:app --reload
```

### Run frontend locally (without Docker)

```bash
cd frontend
npm install
ng serve
```

## Next Steps

- Read the full [README.md](README.md) for detailed information
- Explore the code structure
- Try different domains and difficulty levels
- Customize the AI prompts in `backend/services/openai_service.py`

---

**Happy Interview Preparation! 🚀**
