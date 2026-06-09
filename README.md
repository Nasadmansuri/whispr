# 🫧 Whispr — Say it. Anonymously.

> An anonymous confession and whisper wall built with Django.

**Live Demo:** [whisprapp.pythonanywhere.com](https://whisprapp.pythonanywhere.com)

---

## 📸 Overview

Whispr is a full-stack anonymous social platform where users can post confessions, vote on whispers, comment, join boards, and build a community — all with the option to stay completely anonymous.

---

## ✨ Features

### 🔐 User System
- Register, login, logout
- Email verification (custom SHA256 token)
- Password reset via Gmail SMTP
- Verified badge on profile
- Follow / unfollow users

### 🫧 Whispers (Confessions)
- Post text confessions anonymously or publicly
- Attach images (up to 5MB) or videos (up to 10MB)
- Mood tags — Happy, Sad, Angry
- Post to specific boards or general wall

### 🗳️ Voting & Ranking
- Upvote / downvote system
- Confess Points (CP) — karma earned from upvotes
- Sort by Hot, New, Top, Trending
- Trending algorithm based on last 48 hours

### 💬 Comments
- Nested comments with replies
- Anonymous commenting option
- Delete your own comments

### 🏘️ Boards
- Create community boards (b/college, b/work, etc.)
- Join / leave boards
- Board-specific feed with sort options

### 🛡️ Moderation
- Report system with 5 categories
- Admin ban / unban system
- Rate limiting (max posts per hour)

### 👤 Profiles
- Avatar upload via Cloudinary
- Public whispers on profile
- Confess Points badge (Newcomer, Rising Star, Top Whisperer)
- Follower / following counts

### 📱 Mobile
- Fully responsive design
- Mobile bottom navigation bar
- Dark / light mode toggle

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0.5 |
| Language | Python 3.13 |
| Database | SQLite |
| Media Storage | Cloudinary |
| Frontend | Tailwind CSS (CDN) |
| Email | Gmail SMTP |
| Deployment | PythonAnywhere |
| Version Control | Git + GitHub |

---

## 🚀 Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/Nasadmansuri/whispr.git
cd whispr
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```
SECRET_KEY=your-secret-key
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Run server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

---

## 📁 Project Structure

```
whispr/
├── chupchapbaas/        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── wall/                # Main app
│   ├── models.py        # UserProfile, Confession, Vote, Comment, Board, Report
│   ├── views.py
│   ├── urls.py
│   └── templates/       # All HTML templates
├── templates/
│   └── registration/    # Login, password reset templates
├── manage.py
├── requirements.txt
└── .env                 # Not committed — credentials only
```

---

## ⚙️ Key Technical Notes

- Django 6.0.5 uses `STORAGES` dict instead of `DEFAULT_FILE_STORAGE`
- Email verification uses custom SHA256 token (not Django's default — breaks due to `last_login`)
- Video uploads use `CloudinaryField(resource_type='video')`
- Gmail App Password must have no spaces
- PythonAnywhere free plan blocks outgoing Cloudinary connections

---

## 🌐 Deployment (PythonAnywhere)

1. Clone repo to PythonAnywhere
2. Create virtualenv and install requirements
3. Set up `.env` with credentials
4. Run `python manage.py migrate`
5. Run `python manage.py collectstatic`
6. Configure WSGI file to load `.env` and point to `chupchapbaas.settings`
7. Set virtualenv path in Web tab

---

## 👨‍💻 Developer

**Nasad Mansuri**
- GitHub: [@Nasadmansuri](https://github.com/Nasadmansuri)
- Live: [whisprapp.pythonanywhere.com](https://whisprapp.pythonanywhere.com)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with 🫧 and Django*
