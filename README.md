# Task Manager

A demo-featured task management web application built with Flask, SQLite, and Tailwind CSS. Users can create, edit, delete, and track tasks with priority levels, due dates, and completion status.

## **Setup Instructions**

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package manager)

### **Installation**
1. **Fork and download this repository.**
Next, find the Fork button in the top right of this page. This will allow you to make your own copy. After this, download to your development machine using the green Code button at the top of the repo page.

3. **Create a virtual environment:**
    ```bash
   python -m venv venv

4. **Activate the virtual environment:**

Windows:
```bash
  venv\Scripts\activate
```

macOS/Linux:
```bash
bashsource venv/bin/activate
```
-----------------------------------------------------
**Please Note**
If you are having trouble with activating your virtual environment.
Run the command below and then activate your virtual environment again.
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
----------------------------------------------------------

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. Run the application and initialize the database:
```bash
python app.py
```
______________________________________________________________________________
The app will automatically create the SQLite database and tables on first run.
Access the application:
Open your browser and navigate to: http://127.0.0.1:5000
______________________________________________________________________________
**Please note** I used SQLite [https://sqlitebrowser.org/dl/] to view my database.

**Default Login Credentials**
**Admin Account:**
<br>Username: admin
<br>Password: admin123

**Demo Account:**
<br>Username: demo
<br>Password: demo123
______________________________________________________________________________
**You can find the passwords in the models/user.py or .env file.**
______________________________________________________________________________

## App Structure & Functionality**
**Core Features**

- User Authentication - Register, login, logout with secure sessions
- Task Management - Create, edit, delete, and view tasks
- Task Completion - Mark tasks as complete (one-way flow)
- Priority Levels - High, Medium, Low priority classification
- Due Dates - Set and track task deadlines
- Task Categories - Organize active vs completed tasks
- Statistics - View completion rates and task breakdown

  
```bash
project/
├── controllers/          # Flask blueprints/route handlers
├── models/               # Database models (SQLAlchemy)
├── templates/            # Jinja2 templates
│   ├── admin/            # Admin-related templates
│   ├── auth/             # Authentication templates
│   └── tasks/            # Task management templates
├── app.py                # Main Flask application
├── config.py             # Configuration settings
└── requirements.txt      # Python dependencies
```

## Libraries & Technologies Used**
**Backend**

- Flask - Python web framework
- Flask-SQLAlchemy - Database ORM
- Flask-Login - User session management
- Werkzeug - Password hashing and security
- SQLite - Lightweight database

**Frontend**

- Tailwind CSS - Utility-first CSS framework
- Jinja2 - Template engine (built into Flask)

**Development**

- Python 3.8+ - Programming language

**Development Notes**
This is a demo application designed to showcase Flask development skills and task management functionality. 
The application uses SQLite for simplicity and includes all necessary features for a complete task management system.
