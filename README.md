# 🧩 Kanban_Backend

## 🇬🇧 Description

**Kanban_Backend** is a powerful token-based REST API backend for a Kanban-style project management system. Built using [Django](https://www.djangoproject.com/) and [Django REST Framework](https://www.django-rest-framework.org/), it enables team-based task and board management with clear roles and permissions.

---

## 📦 Installation & Setup

### 🔧 Requirements

- Python 3.9 or higher
- pip (Python package manager)
- virtualenv (optional, recommended)
- Git

### 🚀 Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Kanban_Backend.git
cd Kanban_Backend

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv env
source env/bin/activate  # macOS/Linux
env\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create superuser (optional, for admin access)
python manage.py createsuperuser

# 6. Start development server
python manage.py runserver
```

---

## 🧪 Optional: Admin Interface

You can access the admin interface at `http://127.0.0.1:8000/admin/` to manually manage users, boards, and tasks.

---

## 📮 API Endpoints

| Method  | Endpoint                                   | Description                               |
|--------:|--------------------------------------------|-------------------------------------------|
| `POST`  | `/api/registration/`                       | Register a new user                       |
| `POST`  | `/api/login/`                              | User login (get token)                    |
| `GET`   | `/api/email-check/?email=`                 | Check if email exists                     |
| `GET`   | `/api/boards/`                             | List user’s boards                        |
| `POST`  | `/api/boards/`                             | Create a new board                        |
| `GET`   | `/api/boards/<board_id>/`                  | Get board details                         |
| `PATCH` | `/api/boards/<board_id>/`                  | Update board                              |
| `DELETE`| `/api/boards/<board_id>/`                  | Delete board (owner only)                 |
| `POST`  | `/api/tasks/`                              | Create a new task                         |
| `GET`   | `/api/tasks/assigned-to-me/`               | Get tasks assigned to me                  |
| `GET`   | `/api/tasks/reviewing/`                    | Get tasks I am reviewing                  |
| `PATCH` | `/api/tasks/<task_id>/`                    | Update task                               |
| `DELETE`| `/api/tasks/<task_id>/`                    | Delete task (assignee or reviewer only)   |
| `GET`   | `/api/tasks/<task_id>/comments/`           | Get all comments for a task               |
| `POST`  | `/api/tasks/<task_id>/comments/`           | Add comment to task                       |
| `DELETE`| `/api/tasks/<task_id>/comments/<id>/`      | Delete a comment                          |

---

## 🔐 Authentication

All protected endpoints require a **Token** in the request header:

```http
Authorization: Token <your_token_here>
```

---

## 📁 Project Structure (simplified)

```plaintext
Kanban_Backend/
├── auth_app/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
├── core/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Core Technologies

- Django 5.x
- Django REST Framework
- SQLite

---

## 🧠 Ideas for Future Development

- 🔒 Switch to JWT authentication
- 🌐 Add Swagger / ReDoc API docs
- 📩 Email confirmation on registration
- 📊 Task statistics & dashboard API
- 🔔 Notifications via WebSocket/Channels

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## ✨ Author

**Taylan Umucu**  
📧 oezguer.taylan@umucu.de  
📍 Munich, Germany