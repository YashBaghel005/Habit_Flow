import os
import time
from datetime import date, timedelta
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ── Supabase client (lazy-init so import works without env vars at build time) ─
_supabase: Client | None = None

def get_sb():
    global _supabase
    if _supabase is None:
        url = "https://ugsxvqpnbpbuqsevjdyt.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVnc3h2cXBuYnBidXFzZXZqZHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMyOTg1OTksImV4cCI6MjA4ODg3NDU5OX0.Z6VOGtY99B-KeLdC_XkdKlCk9oYtxLqRJtHpP_rvjD8"
        _supabase = create_client(url, key)

    return _supabase


# ── Default habits seeded per new user ────────────────────────────────────────
DEFAULT_HABITS = [
    {"id": "meditation", "name": "Meditation",             "icon": "🧘",  "category": "Mindfulness", "color": "#a78bfa"},
    {"id": "gym",        "name": "Gym / Workout",           "icon": "💪",  "category": "Fitness",     "color": "#34d399"},
    {"id": "journal",    "name": "Daily Journal",           "icon": "📓",  "category": "Reflection",  "color": "#fbbf24"},
    {"id": "dsa",        "name": "DSA Practice",            "icon": "🧮",  "category": "Revision",    "color": "#f87171"},
    {"id": "ds",         "name": "Data Structures",         "icon": "🗂️", "category": "Revision",    "color": "#60a5fa"},
    {"id": "class",      "name": "Class Notes",             "icon": "📚",  "category": "Revision",    "color": "#fb923c"},
    {"id": "reading",    "name": "Reading",                 "icon": "📖",  "category": "Learning",    "color": "#e879f9"},
    {"id": "water",      "name": "Drink Water (8 glasses)", "icon": "💧",  "category": "Health",      "color": "#38bdf8"},
    {"id": "sleep",      "name": "Sleep 8hrs",              "icon": "😴",  "category": "Health",      "color": "#818cf8"},
    {"id": "no_social",  "name": "No Social Media",         "icon": "🚫",  "category": "Mindfulness", "color": "#fb7185"},
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def require_user_id():
    """Return (uid, None) or (None, error_response_tuple)."""
    uid = None
    if request.method in ("POST", "PUT", "DELETE"):
        body = request.get_json(silent=True) or {}
        uid = body.get("user_id")
    if not uid:
        uid = request.args.get("user_id")
    if not uid:
        return None, (jsonify({"error": "user_id required"}), 401)
    return uid, None


def seed_defaults_if_empty(uid: str):
    """Insert the 10 default habits for a brand-new user (idempotent)."""
    sb = get_sb()
    existing = sb.table("habits").select("id").eq("user_id", uid).limit(1).execute()
    if not existing.data:
        rows = [{**h, "user_id": uid} for h in DEFAULT_HABITS]
        sb.table("habits").insert(rows).execute()


def build_logs_dict(rows: list) -> dict:
    """Convert flat Supabase log rows → {date_str: [habit_id, ...]} for the frontend."""
    result: dict = {}
    for row in rows:
        d = row["log_date"]
        result.setdefault(d, [])
        if row["habit_id"] not in result[d]:
            result[d].append(row["habit_id"])
    return result


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template(
        "index.html",
        supabase_url=os.environ.get("SUPABASE_URL", ""),
        supabase_key=os.environ.get("SUPABASE_KEY", ""),
    )


# ── Habits ────────────────────────────────────────────────────────────────────

@app.route("/api/habits", methods=["GET"])
def get_habits():
    uid, err = require_user_id()
    if err:
        return err
    seed_defaults_if_empty(uid)
    sb = get_sb()
    result = sb.table("habits").select("*").eq("user_id", uid).execute()
    return jsonify(result.data)


@app.route("/api/habits", methods=["POST"])
def add_habit():
    uid, err = require_user_id()
    if err:
        return err
    sb   = get_sb()
    body = request.get_json()
    habit = {
        "id":       f"custom_{str(time.time()).replace('.', '_')}",
        "user_id":  uid,
        "name":     body.get("name", "New Habit"),
        "icon":     body.get("icon", "⭐"),
        "category": body.get("category", "Other"),
        "color":    body.get("color", "#c8ff00"),
    }
    result = sb.table("habits").insert(habit).execute()
    return jsonify(result.data[0] if result.data else habit)


@app.route("/api/habits/<habit_id>", methods=["PUT"])
def edit_habit(habit_id):
    uid, err = require_user_id()
    if err:
        return err
    sb      = get_sb()
    body    = request.get_json()
    updates = {k: body[k] for k in ("name", "icon", "category", "color") if k in body}
    result  = (
        sb.table("habits")
        .update(updates)
        .eq("id", habit_id)
        .eq("user_id", uid)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "not found"}), 404
    return jsonify(result.data[0])


@app.route("/api/habits/<habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    uid, err = require_user_id()
    if err:
        return err
    sb = get_sb()
    sb.table("habits").delete().eq("id", habit_id).eq("user_id", uid).execute()
    return jsonify({"success": True})


# ── Logs ──────────────────────────────────────────────────────────────────────

@app.route("/api/log", methods=["POST"])
def log_habit():
    uid, err = require_user_id()
    if err:
        return err
    sb       = get_sb()
    body     = request.get_json()
    habit_id = body.get("habit_id")
    log_date = body.get("date", str(date.today()))

    existing = (
        sb.table("logs")
        .select("id")
        .eq("user_id",  uid)
        .eq("habit_id", habit_id)
        .eq("log_date", log_date)
        .execute()
    )
    if existing.data:
        sb.table("logs").delete().eq("id", existing.data[0]["id"]).execute()
        status = "removed"
    else:
        sb.table("logs").insert({
            "user_id":  uid,
            "habit_id": habit_id,
            "log_date": log_date,
        }).execute()
        status = "added"

    return jsonify({"status": status, "date": log_date, "habit_id": habit_id})


@app.route("/api/logs", methods=["GET"])
def get_logs():
    uid, err = require_user_id()
    if err:
        return err
    sb     = get_sb()
    result = sb.table("logs").select("habit_id,log_date").eq("user_id", uid).execute()
    return jsonify(build_logs_dict(result.data))


@app.route("/api/today", methods=["GET"])
def get_today():
    uid, err = require_user_id()
    if err:
        return err
    sb     = get_sb()
    today  = str(date.today())
    result = (
        sb.table("logs")
        .select("habit_id")
        .eq("user_id",  uid)
        .eq("log_date", today)
        .execute()
    )
    return jsonify([row["habit_id"] for row in result.data])


@app.route("/api/stats", methods=["GET"])
def get_stats():
    uid, err = require_user_id()
    if err:
        return err
    sb = get_sb()

    habits_res = sb.table("habits").select("id").eq("user_id", uid).execute()
    logs_res   = sb.table("logs").select("habit_id,log_date").eq("user_id", uid).execute()

    logs_dict = build_logs_dict(logs_res.data)
    today     = date.today()
    stats     = {}

    for habit in habits_res.data:
        hid   = habit["id"]
        total = sum(1 for ids in logs_dict.values() if hid in ids)

        # current streak
        streak = 0
        check  = today
        while True:
            ds = str(check)
            if ds in logs_dict and hid in logs_dict[ds]:
                streak += 1
                check  -= timedelta(days=1)
            else:
                break

        # 365-day heatmap
        heatmap = {
            str(today - timedelta(days=i)):
            1 if str(today - timedelta(days=i)) in logs_dict
                and hid in logs_dict[str(today - timedelta(days=i))]
            else 0
            for i in range(365)
        }

        stats[hid] = {"streak": streak, "total": total, "heatmap": heatmap}

    return jsonify(stats)


# ── Vercel: do NOT call app.run() at module level ─────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
