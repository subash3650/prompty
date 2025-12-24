# Prompty Challenge

A real-time competitive prompt injection challenge platform where participants strategically craft prompts to extract secret passwords from an AI opponent (Gandalf).

## 🎮 Features

- **8 Progressive Levels** - From no defense to adaptive AI guards
- **Real-time Leaderboard** - Compete against other players
- **Groq AI Integration** - Fast 0.5-1.5 second responses
- **Dark Theme UI** - Modern, responsive design
- **JWT Authentication** - Secure user sessions

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your Groq API key
copy .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here

# Run the server
python -m uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎯 How to Play

1. **Register** - Create an account
2. **Play** - Submit prompts to Gandalf to extract the secret password
3. **Progress** - Pass each level to unlock the next
4. **Compete** - Climb the leaderboard by reaching higher levels faster

## 🛡️ Level Defenses

| Level | Input Guard | Output Guard | Difficulty |
|-------|-------------|--------------|------------|
| 1 | None | None | ⭐ |
| 2 | None | System prompt | ⭐⭐ |
| 3 | None | Exact match | ⭐⭐⭐ |
| 4 | None | Semantic | ⭐⭐⭐⭐ |
| 5 | Intent | Semantic | ⭐⭐⭐⭐ |
| 6 | Semantic | Combined | ⭐⭐⭐⭐⭐ |
| 7 | Combined | Combined | ⭐⭐⭐⭐⭐ |
| 8 | Combined | Combined | ⭐⭐⭐⭐⭐⭐ |

## 🏗️ Tech Stack

**Frontend**
- Next.js 14 (App Router)
- React 18 + TypeScript
- TailwindCSS
- Zustand (State Management)

**Backend**
- FastAPI (Python)
- SQLAlchemy + SQLite
- JWT Authentication
- Groq AI API

## 📁 Project Structure

```
prompty/
├── backend/
│   ├── app/
│   │   ├── ai/           # Groq client
│   │   ├── guards/       # Input/output guards
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routes/       # API endpoints
│   │   ├── schemas/      # Pydantic models
│   │   ├── security/     # JWT, password, rate limit
│   │   └── services/     # Business logic
│   ├── main.py           # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API client
│   │   └── store/        # Zustand stores
│   └── package.json
└── README.md
```

## 🔧 Configuration

### Backend (.env)

```env
DATABASE_URL=sqlite:///./prompty.db
JWT_SECRET=your-secret-key-32-chars-minimum
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=mixtral-8x7b-32768
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login |
| POST | /api/auth/logout | Logout |
| GET | /api/game/status | Get game status |
| POST | /api/game/submit-prompt | Submit prompt |
| GET | /api/leaderboard | Get leaderboard |
| GET | /api/users/me | Get profile |

## 📄 License

MIT License - Built for educational purposes.
