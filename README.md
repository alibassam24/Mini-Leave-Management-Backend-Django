# 📝 Mini Leave Management System (Django REST API)

A simple Leave Management System built with **Django REST Framework**
It allows HR to manage employees and leave requests with secure APIs.  

MAKE SURE TO READ SETUP INSTRUCTIONS 👇

---

## 🚀 Main Features (in simple terms)

- 👩‍💼 **HR Management**  
  HR can add new employees and manage their profiles.

- 🧑‍💻 **Employee Management**  
  Employees can apply for leave and track their leave balance.

- 📨 **Leave Requests**  
  Employees apply for leave → HR approves/rejects → Leave balance auto-updates.

- 🔐 **Authentication**  
  Login/Logout with secure JWT tokens. Only HR has management privileges.

- 📊 **Leave Balance Tracking**  
  Each employee has leave balance updated automatically after approvals.

---

## 📂 API Endpoints

Here’s a quick reference of all available endpoints:

### 🔑 Authentication

| Method | Endpoint        | Description           |
|--------|----------------|-----------------------|
| POST   | `/api/login/`  | Login and get JWT     |
| POST   | `/api/logout/` | Logout (invalidate)   |

### 👩‍💼 HR Management

| Method | Endpoint       | Description            |
|--------|----------------|------------------------|
| POST   | `/api/hr/add/` | Add a new HR account   |

### 🧑‍💻 Employee Management

| Method | Endpoint             | Description        |
|--------|----------------------|--------------------|
| POST   | `/api/employee/add/`    | Add new employee  |
| DELETE | `/api/employee/delete/` | Delete employee   |

### 📨 Leave Management

| Method | Endpoint                                      | Description                |
|--------|-----------------------------------------------|----------------------------|
| POST   | `/api/leave/apply/`                           | Apply for leave            |
| GET    | `/api/leave/applications/`                    | View all leave applications|
| PATCH  | `/api/leave/approve/<application_id>/`        | Approve leave              |
| PATCH  | `/api/leave/reject/<application_id>/`         | Reject leave               |
| GET    | `/api/leave/balance/<employee_id>/`           | Get leave balance          |

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **Django 4.x**
- **Django REST Framework**
- **Token Authentication**
- **SQLite (default, can upgrade to PostgreSQL/MySQL)**

---

## 🔧 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/alibassam24/Mini-Leave-Management-Backend-Django.git
cd Mini-Leave-Management-Backend-Django

# Create virtual environment
python -m venv env
source env/bin/activate  # For Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

#Write secret key
⚙️ Environment Setup

#Generate your own Django SECRET_KEY:

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

#In the project root, create a .env file:
#Example .env:

SECRET_KEY="(secret key generated)"


#Copy this key into your .env.

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start development server
python manage.py runserver
```

##  🙋‍♂️ Author 

Ali Bassam
📧 alibassam063@gmail.com
🔗 www.linkedin/in/alibassam1