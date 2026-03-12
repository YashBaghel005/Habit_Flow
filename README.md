# HabitFlow — Habit Tracker with Analytics

HabitFlow is a **modern habit tracking web application** that helps users build consistency through visual analytics like streak tracking, monthly matrices, and activity heatmaps.

It uses **Flask for the backend** and **Supabase for authentication and database**, with a clean interactive frontend built in HTML, CSS, and JavaScript.

---

# Live Demo

*(Add your Vercel deployment link here)*

```
https://your-project-name.vercel.app
```

---

# Features

* Secure user authentication using Supabase
* Create, edit, and delete habits
* Daily habit completion tracking
* Automatic habit streak calculation
* Monthly habit matrix dashboard
* Yearly activity heatmap
* Progress analytics and charts
* Modern responsive UI

---

# Tech Stack

### Backend

* Python
* Flask

### Frontend

* HTML
* CSS
* JavaScript
* Chart.js

### Database & Auth

* Supabase

### Deployment

* Vercel

---

# Project Structure

```
habitflow
│
├── app.py
├── templates
│   └── index.html
│
├── requirements.txt
├── vercel.json
└── README.md
```

* `app.py` → Flask backend handling APIs and database operations
* `templates/index.html` → Frontend UI and authentication logic
* `requirements.txt` → Python dependencies 
* `vercel.json` → Vercel deployment configuration 

---

# Installation (Run Locally)

### 1 Clone the repository

```
git clone https://github.com/YOUR_USERNAME/Habit_Flow.git
cd Habit_Flow
```

---

### 2 Install dependencies

```
pip install -r requirements.txt
```

Dependencies include Flask, Supabase Python client, and python-dotenv. 

---

### 3 Create environment variables

Create a `.env` file in the root folder.

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

The backend loads these variables automatically using `python-dotenv`. 

---

### 4 Run the application

```
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

# Database Setup

In Supabase SQL Editor run:

```
CREATE TABLE habits (
  id TEXT PRIMARY KEY,
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  icon TEXT,
  category TEXT,
  color TEXT
);

CREATE TABLE logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  habit_id TEXT NOT NULL,
  log_date DATE NOT NULL
);
```

Row Level Security (RLS) should be enabled so users only see their own habits.

---

# Deployment

This project is deployed using **Vercel serverless Python runtime**.

The configuration in `vercel.json` routes all requests to the Flask app. 

To deploy:

1. Push the repository to GitHub
2. Import the repo in **Vercel**
3. Add environment variables:

```
SUPABASE_URL
SUPABASE_KEY
```

4. Deploy

---

# Security Notes

* Supabase **Row Level Security (RLS)** protects user data
* The application uses the **Supabase anon public key**, which is safe for frontend usage
* Each API request includes the authenticated user's ID

---

# Author

**Yash Baghel**

GitHub
[https://github.com/YashBaghel005](https://github.com/YashBaghel005)


