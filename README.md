# SmartKoach - AI-Based Personalized Interview Preparation & Feedback System

## 📖 Project Overview

SmartKoach is an AI-powered interview preparation system designed to help students and professionals practice technical interviews with real-time feedback. The system uses OpenAI to simulate realistic interview scenarios and provide constructive feedback on answers.

## 🎯 Problem Statement

Technical interviews are challenging, and many candidates struggle due to lack of practice and personalized feedback. SmartKoach addresses this by:

- Providing on-demand interview practice sessions
- Offering domain-specific technical questions (DSA, ML, DBMS, OS)
- Delivering immediate, AI-powered feedback
- Adjusting difficulty levels based on user preference
- Maintaining professional interview tone and structure

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User (Browser)                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ HTTP
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Angular Frontend (Port 4200)                │
│                                                          │
│  - Chat Interface                                        │
│  - Domain/Difficulty Selection                           │
│  - Message History Display                               │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ REST API
                        │
┌───────────────────────▼─────────────────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│                                                          │
│  - POST /chat - Handle interview interactions            │
│  - POST /reset - Reset conversation                      │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ API Call
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   OpenAI API (gpt-3.5-turbo)             │
│                                                          │
│  - Generate interview questions                          │
│  - Evaluate user answers                                 │
│  - Provide structured feedback                           │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: Angular 17
- **Language**: TypeScript
- **Styling**: CSS3
- **HTTP Client**: Angular HttpClient
- **Server**: Nginx (in production container)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11
- **AI Integration**: OpenAI API
- **ASGI Server**: Uvicorn
- **Environment Management**: python-dotenv

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx

### AI Model
- **Provider**: OpenAI
- **Model**: gpt-3.5-turbo
- **Purpose**: Interview question generation and answer evaluation

## 📋 Prerequisites

Before running SmartKoach, ensure you have:

1. **Docker** (version 20.10 or higher)
2. **Docker Compose** (version 2.0 or higher)
3. **OpenAI API Key** (Get it from [OpenAI Platform](https://platform.openai.com/api-keys))

## 🚀 How to Run

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Backend/smartkoach
```

### Step 2: Configure Environment Variables

Create a `.env` file in the `smartkoach/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

⚠️ **Important**: Never commit the `.env` file to version control!

### Step 3: Build and Run with Docker Compose

```bash
# Build the containers
docker compose build

# Start the services
docker compose up
```

This will:
- Build the backend Docker image (Python/FastAPI)
- Build the frontend Docker image (Angular/Nginx)
- Start both services
- Backend will be available at `http://localhost:8000`
- Frontend will be available at `http://localhost:4200`

### Step 4: Access the Application

Open your browser and navigate to:

```
http://localhost:4200
```

### Step 5: Start Your Interview Practice

1. Select a **Domain** (DSA, ML, DBMS, or OS)
2. Select a **Difficulty** level (Easy, Medium, or Hard)
3. Type your message or answer in the chat box
4. Click **Send** or press **Enter**
5. Review the AI feedback and continue the conversation

## 🎮 Usage Guide

### Starting an Interview

When you first open SmartKoach, the AI will greet you. You can:

- Ask for a question: "Give me a medium-level DSA question"
- Answer a question: Provide your solution or approach
- Request clarification: "Can you explain that concept?"
- Change topics: Switch domain and difficulty at any time

### Example Interaction

```
You: "Give me a medium-level DSA question on arrays"

SmartKoach: "Sure! Here's a medium-level question:

Given an array of integers, find two numbers that add up to a specific target. 
Return the indices of the two numbers.

Example: Input: [2, 7, 11, 15], target = 9
Output: [0, 1] (because 2 + 7 = 9)

How would you approach this problem?"

You: "I would use a hash map to store the numbers I've seen so far..."

SmartKoach: "Great approach! Using a hash map is an efficient solution..."
```

### Resetting the Conversation

Click the **Reset Chat** button to:
- Clear conversation history
- Start fresh with new topics
- Reset the AI context

## 📁 Project Structure

```
smartkoach/
│
├── docker-compose.yml          # Docker orchestration configuration
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── backend/                    # FastAPI backend
│   ├── Dockerfile              # Backend container configuration
│   ├── requirements.txt        # Python dependencies
│   ├── main.py                 # FastAPI application entry point
│   └── services/
│       └── openai_service.py   # OpenAI API integration service
│
└── frontend/                   # Angular frontend
    ├── Dockerfile              # Frontend container configuration
    ├── nginx.conf              # Nginx server configuration
    ├── package.json            # Node.js dependencies
    ├── angular.json            # Angular CLI configuration
    ├── tsconfig.json           # TypeScript configuration
    ├── tsconfig.app.json       # App-specific TypeScript config
    └── src/
        ├── index.html          # HTML entry point
        ├── main.ts             # Angular bootstrap file
        └── app/
            ├── app.component.ts    # Main component logic
            ├── app.component.html  # Main component template
            └── app.component.css   # Main component styles
```

## 🔌 API Endpoints

### Backend API

#### GET `/`
- **Description**: Health check endpoint
- **Response**: `{"message": "SmartKoach API is running", "status": "ok"}`

#### POST `/chat`
- **Description**: Send a message to the AI interview coach
- **Request Body**:
  ```json
  {
    "message": "Your answer or question",
    "domain": "DSA",
    "difficulty": "Medium"
  }
  ```
- **Response**:
  ```json
  {
    "reply": "AI generated interview feedback"
  }
  ```

#### POST `/reset`
- **Description**: Reset the conversation history
- **Response**: `{"message": "Conversation reset successfully"}`

## 🐛 Troubleshooting

### Backend not starting

**Issue**: Backend container fails to start

**Solutions**:
1. Check if `.env` file exists and contains valid `OPENAI_API_KEY`
2. Verify API key is correct at [OpenAI Platform](https://platform.openai.com/api-keys)
3. Check Docker logs: `docker compose logs backend`

### Frontend not loading

**Issue**: Frontend shows blank page

**Solutions**:
1. Check if backend is running: `http://localhost:8000/`
2. Clear browser cache and reload
3. Check Docker logs: `docker compose logs frontend`
4. Verify port 4200 is not in use: `lsof -i :4200`

### CORS errors

**Issue**: Frontend cannot connect to backend

**Solutions**:
1. Ensure backend CORS settings allow `http://localhost:4200`
2. Restart both containers: `docker compose restart`

### API rate limiting

**Issue**: OpenAI API returns rate limit errors

**Solutions**:
1. Wait a few minutes before retrying
2. Check your API quota at OpenAI Platform
3. Consider using a different API key if available

## 🔒 Security Notes

⚠️ **This is a college demonstration project, NOT production-ready!**

For production use, you would need to add:
- User authentication and authorization
- API key rotation and secure storage (e.g., AWS Secrets Manager)
- Rate limiting and request throttling
- Input sanitization and validation
- HTTPS/TLS encryption
- Database for persistent storage
- Logging and monitoring
- Error tracking
- Security headers and CSP

## 🚀 Future Scope

Potential enhancements for this project:

1. **Voice Input/Output**
   - Add Speech-to-Text for voice answers
   - Text-to-Speech for AI responses

2. **Progress Tracking**
   - SQLite database for storing sessions
   - Performance analytics and scoring
   - Progress visualization with charts

3. **Advanced Features**
   - Code execution environment
   - Whiteboard for diagrams
   - Multiple interview rounds
   - Peer comparison and leaderboards

4. **Enhanced AI**
   - Fine-tuned models for specific domains
   - Multi-modal support (code, diagrams)
   - Personality-based interviewer modes

5. **Collaboration**
   - Multi-user mock interviews
   - Peer review system
   - Mentor feedback integration

6. **Mobile App**
   - Native iOS/Android applications
   - Offline mode support

## 👥 Team & Contributions

This project was created as a college demonstration of AI integration in web applications.

**Key Learning Outcomes**:
- Full-stack application development
- Docker containerization
- RESTful API design
- AI/ML integration
- Modern web frameworks (Angular, FastAPI)

## 📄 License

This project is created for educational purposes.

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- FastAPI framework for excellent Python API development
- Angular team for the powerful frontend framework
- Docker for containerization technology

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `docker compose logs`
3. Verify all prerequisites are met
4. Ensure environment variables are correctly set

---

**Built with ❤️ for learning and demonstration purposes**
