# UpArch 📦

A lightweight, self-hosted file storage service. Take control of your files — no third-party services, no storage limits imposed by others.

---

## 🚦 Project Status

> **Backend and Frontend completed ✅**

| Feature | Status |
|---|---|
| User authentication (JWT) | ✅ Complete |
| File upload | ✅ Complete |
| File listing | ✅ Complete |
| File download | ✅ Complete |
| File deletion | ✅ Complete |
| Frontend (UI) | ✅ Complete |
| Docker deployment | 📋 Pending |

---

## ✨ Features

### v1 (current)
- 🔐 User login with username and password
- ⬆️ File upload
- 📄 View uploaded files (list or grid)
- ⬇️ File download

### Planned
- 📁 Folder creation and file organization
- 🔗 Share files via public link
- 🛠️ Admin panel
- 👁️ File preview (images, PDF, video)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI |
| Database | SQLite |
| Frontend | HTML + CSS + JavaScript |
| Deployment | Docker + Docker Compose |

---

## 🚀 Installation

### Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/KilianCuadrado/uparch.git
cd uparch

# 2. Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Initialize database
python backend/database.py

# 4. Start the development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 5. Open your browser
# API Documentation: http://localhost:8000/docs
# Frontend: http://localhost:8000 (coming soon)
```

### Create First User

```bash
python3
```

```python
from backend.database import get_connection
from backend.auth import hash_password

conn = get_connection()
cursor = conn.cursor()

username = "admin"
password = "1234"
hashed = hash_password(password)

cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (username, hashed))
conn.commit()
conn.close()
exit()
```

### Docker Setup (Coming Soon)

```bash
# Build and run with Docker Compose
docker compose up -d

# Access the application
http://localhost:8000
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).