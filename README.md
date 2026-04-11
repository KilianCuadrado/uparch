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
| Docker deployment | ✅ Complete |

---

## ✨ Features

### v1 Complete
- 🔐 User login with username and password
- 🎨 Modern Web Interface (Vanilla JS) with Drag & Drop
- ⬆️ File upload(Limited to 10MB)
- 📄 View uploaded files (list or grid)
- ⬇️ File download
- 🗑️ File deletion

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

### 🐳 Using Docker (Recommended)

The easiest way to run UpArch is using Docker. This ensures that the frontend and backend are completely isolated and ready to go in seconds.

```bash
# 1. Clone the repository
git clone https://github.com/KilianCuadrado/uparch.git
cd uparch

# 2. Build and start the services
docker compose up --build -d
```

Once running, access the application at:
- **Frontend (Web):** http://localhost:5000
- **API Documentation:** http://localhost:8000/docs

> **💡 Default Account:** By default, an initial administrator account is automatically generated for you.  
> **Username:** `admin`  
> **Password:** `1234`

### 🛠️ Manual Development Setup (Without Docker)

<details>
<summary>Click to view manual installation steps</summary>

```bash
# 1. Start the backend
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python database.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Serve the frontend (in a new terminal)
cd frontend
python3 -m http.server 8080
```
</details>

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
