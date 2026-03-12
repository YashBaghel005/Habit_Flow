# HabitFlow — Supabase + Vercel Deployment Guide

---

## 1. Set Up Supabase

### 1a. Create a project
1. Go to https://supabase.com and sign in
2. Click **New Project**, give it a name (e.g. `habitflow`), set a DB password, choose a region
3. Wait ~2 minutes for provisioning

### 1b. Create the database tables
Go to **SQL Editor** in your Supabase dashboard and run:

```sql
-- Habits table
CREATE TABLE habits (
  id        TEXT PRIMARY KEY,
  user_id   UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name      TEXT NOT NULL,
  icon      TEXT NOT NULL DEFAULT '⭐',
  category  TEXT NOT NULL DEFAULT 'Other',
  color     TEXT NOT NULL DEFAULT '#c8ff00'
);

-- Logs table
CREATE TABLE logs (
  id         BIGSERIAL PRIMARY KEY,
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  habit_id   TEXT NOT NULL,
  log_date   DATE NOT NULL,
  UNIQUE (user_id, habit_id, log_date)
);

-- Row Level Security (RLS) — each user only sees their own rows
ALTER TABLE habits ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs   ENABLE ROW LEVEL SECURITY;

CREATE POLICY "habits: user owns their rows"
  ON habits FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "logs: user owns their rows"
  ON logs FOR ALL USING (auth.uid() = user_id);
```

### 1c. Get your API credentials
In Supabase → **Project Settings → API**:
- Copy **Project URL** → this is `SUPABASE_URL`
- Copy **anon / public** key → this is `SUPABASE_KEY`

### 1d. Disable email confirmation (optional, for easier local testing)
In Supabase → **Authentication → Email** → turn off **Confirm email**.
This lets users sign up and immediately sign in without clicking a confirmation link.

---

## 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create a .env file (do NOT commit this)
echo "SUPABASE_URL=https://xxxx.supabase.co" >> .env
echo "SUPABASE_KEY=eyJhbGc..." >> .env

# Run locally
python app.py
# → http://localhost:5000
```

> The app reads `SUPABASE_URL` and `SUPABASE_KEY` from environment variables.
> Locally you can also use `python-dotenv` — it's already in requirements.txt.

To load `.env` automatically, add this at the top of `app.py` (already included):
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 3. Deploy to Vercel

### 3a. Install the Vercel CLI
```bash
npm install -g vercel
```

### 3b. Login and link your project
```bash
vercel login
cd habitflow/
vercel
```
Follow the prompts. When asked about settings, accept the defaults — the `vercel.json` handles everything.

### 3c. Set environment variables on Vercel
```bash
vercel env add SUPABASE_URL
# paste your Supabase URL when prompted

vercel env add SUPABASE_KEY
# paste your Supabase anon key when prompted
```

Or set them in the Vercel dashboard:
**Project → Settings → Environment Variables**

### 3d. Deploy to production
```bash
vercel --prod
```

Your app is now live at `https://your-project.vercel.app` 🚀

---

## 4. Project Structure

```
habitflow/
├── app.py              ← Flask backend (Supabase, all API routes)
├── requirements.txt    ← Python dependencies
├── vercel.json         ← Vercel deployment config
└── templates/
    └── index.html      ← Full SPA frontend (auth + app UI)
```

---

## 5. How Auth Works

| Step | What happens |
|------|-------------|
| User opens the app | `initAuth()` calls `supabase.auth.getSession()` |
| Session exists | App loads directly — no login screen shown |
| No session | Login/Sign-up screen is shown |
| User signs in | Supabase returns a session; `user_id` stored in memory |
| Every API call | `user_id` appended as query param or JSON body field |
| Flask backend | Reads `user_id`, filters all Supabase queries by it |
| User logs out | Session cleared, login screen shown again |

---

## 6. Security Notes

- **Row Level Security (RLS)** is enabled on both tables — even if someone crafts a malicious API call with another user's `user_id`, Supabase will reject it at the DB level.
- The `SUPABASE_KEY` used is the **anon** (public) key, which is safe to expose in the browser — RLS policies enforce access control.
- Never use the **service_role** key in the frontend.
- The Flask backend uses the anon key too; if you want server-side admin operations (e.g. deleting a user), use the service_role key only in backend code via a separate env var.

---

## 7. Troubleshooting

| Problem | Fix |
|---------|-----|
| `SUPABASE_URL and SUPABASE_KEY must be set` | Set env vars locally in `.env` or on Vercel |
| Sign-up works but can't log in | Disable email confirmation in Supabase Auth settings |
| "user_id required" 401 errors | User is not logged in — check session in browser console |
| Habits not loading | Check RLS policies are created correctly |
| Vercel build fails | Make sure `requirements.txt` is in the root of the project |
