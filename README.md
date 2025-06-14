# 💼 R2OL.ai – Resume to Offer Letter AI Platform

R2OL.ai is a full-stack AI platform that helps job seekers go from **resume** to **offer letter** faster with smart recommendations and automation. This guide helps you set up the project locally and contribute efficiently.

---

## 📁 Project Structure


r2ol-ai/
├── backend/ # FastAPI backend

│ ├── server.py

│ ├── requirements.txt

│ └── .env

├── frontend/ # React frontend

│ ├── src/

│ ├── package.json

│ └── .env

└── README.md # This file

yaml
Copy
Edit

---

## 🧑‍💻 Local Development Setup

### 🔧 Prerequisites

- Python 3.8+
- Node.js & npm
- MongoDB (local installation)
- Gemini API Key (from Google AI)

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Hustlerkrishna1/r2ol-ai.git
cd r2ol-ai
2️⃣ Backend Setup (FastAPI)
bash
Copy
Edit
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
Create backend/.env:

env
Copy
Edit
MONGO_URL=mongodb://localhost:27017
DB_NAME=r2ol_database
GEMINI_API_KEY=your_actual_api_key_here
Run the backend server:

bash
Copy
Edit
uvicorn server:app --reload --host 0.0.0.0 --port 8001
3️⃣ Frontend Setup (React)
bash
Copy
Edit
# Open a new terminal
cd frontend

# Install dependencies
npm install
Create frontend/.env:

env
Copy
Edit
REACT_APP_BACKEND_URL=http://localhost:8001
Start the React app:

bash
Copy
Edit
npm start
4️⃣ MongoDB Setup
Install MongoDB if not already installed:

Windows/macOS: Download from mongodb.com

macOS (Homebrew):

bash
Copy
Edit
brew tap mongodb/brew
brew install mongodb-community
Ubuntu:

bash
Copy
Edit
sudo apt update
sudo apt install mongodb
Start MongoDB service:

bash
Copy
Edit
sudo systemctl start mongod
🌐 Access the App
Frontend: http://localhost:3000

Backend API: http://localhost:8001/api

🔒 Environment Variables
backend/.env:
env
Copy
Edit
MONGO_URL=mongodb://localhost:27017
DB_NAME=r2ol_database
GEMINI_API_KEY=your_actual_api_key_here
frontend/.env:
env
Copy
Edit
REACT_APP_BACKEND_URL=http://localhost:8001
✅ Benefits of Local Setup
⚡ Faster development with hot-reloads

🌐 No sleeping apps like on free hosts

🔍 Complete debugging & logging access

🔧 Offline capable development

💻 Full control over environment

🔐 Git Best Practices
bash
Copy
Edit
# Add ignore rules
echo "*.env" >> .gitignore
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore

# Commit changes
git add .
git commit -m "Initial R2OL.ai MVP implementation"
git push origin main
🚀 Production Deployment (Coming Soon)
Dockerize backend & frontend

Use production-ready MongoDB Atlas

Setup environment configs securely

Enable CORS, HTTPS, and logging

Deploy to platforms like Vercel + Render or Azure

🤝 Contributing
Have an idea, suggestion, or want to improve this project? Contributions are welcome! Please fork the repo and open a PR.

📄 License
MIT License – feel free to use and modify with attribution.

✨ Credits
Created by Hustlerkrishna1
Built with 💻 FastAPI, React, MongoDB, and Google Gemini

