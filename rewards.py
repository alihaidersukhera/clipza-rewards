"""Clipza Rewards — rewards backend: campaigns, submissions, earnings (SQLite)."""
import os
import sqlite3
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "clipza_rewards.db")


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand_name TEXT NOT NULL,
                rate_per_1k REAL NOT NULL,
                min_views INTEGER NOT NULL DEFAULT 1000,
                cap_per_clip INTEGER NOT NULL DEFAULT 0,
                budget REAL NOT NULL DEFAULT 0,
                rules TEXT DEFAULT '',
                status TEXT DEFAULT 'live',
                created_at REAL
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                clipper_name TEXT NOT NULL,
                platform TEXT NOT NULL,
                post_url TEXT NOT NULL,
                clip_path TEXT DEFAULT '',
                reported_views INTEGER NOT NULL DEFAULT 0,
                verified_views INTEGER NOT NULL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                earnings REAL DEFAULT 0,
                submitted_at REAL,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )""")


# ---------------------------------------------------------------- campaigns --
def create_campaign(name, brand_name, rate_per_1k, min_views, cap_per_clip,
                    budget, rules=""):
    with _db() as conn:
        cur = conn.execute(
            """INSERT INTO campaigns
               (name, brand_name, rate_per_1k, min_views, cap_per_clip, budget,
                rules, status, created_at)
               VALUES (?,?,?,?,?,?,?,'live',?)""",
            (name, brand_name, float(rate_per_1k), int(min_views),
             int(cap_per_clip), float(budget), rules, time.time()))
        return cur.lastrowid


def list_campaigns(status=None):
    with _db() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM campaigns WHERE status=? ORDER BY id DESC",
                (status,)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM campaigns ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def get_campaign(campaign_id):
    with _db() as conn:
        row = conn.execute("SELECT * FROM campaigns WHERE id=?",
                           (campaign_id,)).fetchone()
    return dict(row) if row else None


def set_campaign_status(campaign_id, status):
    with _db() as conn:
        conn.execute("UPDATE campaigns SET status=? WHERE id=?",
                     (status, campaign_id))


# --------------------------------------------------------------- submissions --
def submit_clip(campaign_id, clipper_name, platform, post_url, reported_views,
                clip_path=""):
    with _db() as conn:
        cur = conn.execute(
            """INSERT INTO submissions
               (campaign_id, clipper_name, platform, post_url, clip_path,
                reported_views, verified_views, status, earnings, submitted_at)
               VALUES (?,?,?,?,?,?,0,'pending',0,?)""",
            (campaign_id, clipper_name, platform, post_url, clip_path,
             int(reported_views), time.time()))
        return cur.lastrowid


def list_submissions(campaign_id=None, status=None, clipper=None):
    with _db() as conn:
        q = "SELECT * FROM submissions"
        clauses, params = [], []
        if campaign_id:
            clauses.append("campaign_id=?")
            params.append(campaign_id)
        if status:
            clauses.append("status=?")
            params.append(status)
        if clipper:
            clauses.append("LOWER(TRIM(clipper_name))=LOWER(TRIM(?))")
            params.append(clipper)
        if clauses:
            q += " WHERE " + " AND ".join(clauses)
        q += " ORDER BY id DESC"
        rows = conn.execute(q, params).fetchall()
    return [dict(r) for r in rows]


def calc_earnings(campaign, verified_views):
    if verified_views < campaign["min_views"]:
        return 0.0
    views = verified_views
    if campaign["cap_per_clip"] and views > campaign["cap_per_clip"]:
        views = campaign["cap_per_clip"]
    return round(views / 1000.0 * campaign["rate_per_1k"], 2)


def review_submission(submission_id, verified_views, approve=True):
    with _db() as conn:
        sub = conn.execute("SELECT * FROM submissions WHERE id=?",
                           (submission_id,)).fetchone()
        if not sub:
            raise ValueError("Submission not found")
        campaign = get_campaign(sub["campaign_id"])
        earnings = calc_earnings(campaign, int(verified_views)) if approve else 0.0
        status = "approved" if approve else "rejected"
        conn.execute(
            """UPDATE submissions SET verified_views=?, status=?, earnings=?
               WHERE id=?""",
            (int(verified_views), status, earnings, submission_id))
        return earnings


# ------------------------------------------------------------------- stats ---
def campaign_stats(campaign_id):
    subs = list_submissions(campaign_id=campaign_id)
    approved = [s for s in subs if s["status"] == "approved"]
    pending = [s for s in subs if s["status"] == "pending"]
    total_views = sum(s["verified_views"] for s in approved)
    spent = round(sum(s["earnings"] for s in approved), 2)
    campaign = get_campaign(campaign_id)
    remaining = (round(campaign["budget"] - spent, 2)
                 if campaign and campaign["budget"] else None)
    return {"submissions": len(subs), "approved": len(approved),
            "pending": len(pending), "total_views": total_views,
            "spent": spent, "remaining": remaining}


def platform_totals():
    with _db() as conn:
        row = conn.execute("""
            SELECT COUNT(DISTINCT campaign_id) AS campaigns,
                   SUM(CASE WHEN status='approved' THEN earnings ELSE 0 END) AS paid,
                   SUM(CASE WHEN status='approved' THEN verified_views ELSE 0 END) AS views
            FROM submissions""").fetchone()
    d = dict(row)
    return {"campaigns": d["campaigns"] or 0, "paid": round(d["paid"] or 0, 2),
            "views": d["views"] or 0}


def leaderboard():
    with _db() as conn:
        rows = conn.execute("""
            SELECT clipper_name, COUNT(*) AS clips,
                   SUM(verified_views) AS views, SUM(earnings) AS earnings
            FROM submissions WHERE status='approved'
            GROUP BY clipper_name ORDER BY earnings DESC LIMIT 20""").fetchall()
    return [dict(r) for r in rows]


def load_demo_data():
    c1 = create_campaign(
        "DEMO: TechGadget Launch", "DemoBrand", rate_per_1k=1.5,
        min_views=1000, cap_per_clip=500000, budget=1000,
        rules="1. Clip must come from the launch video.\n"
              "2. Minimum 10 seconds, vertical 9:16.\n"
              "3. Organic views only — no bots.\n"
              "4. Tag @demobrand in the caption.")
    c2 = create_campaign(
        "DEMO: FitFuel Challenge", "FitFuel", rate_per_1k=2.0,
        min_views=2000, cap_per_clip=1000000, budget=2000,
        rules="1. Show the product in the first 3 seconds.\n"
              "2. Add #fitfuel to the caption.\n"
              "3. Minimum 2,000 views to count.")
    c3 = create_campaign(
        "DEMO: TravelVibes Clips", "TravelVibes", rate_per_1k=1.0,
        min_views=500, cap_per_clip=250000, budget=500,
        rules="1. Any travel moment from the source video.\n"
              "2. Keep it under 45 seconds.")
    s = []
    s.append(submit_clip(c1, "clip_queen", "TikTok",
                         "https://tiktok.com/@demo/video/101", 45200))
    s.append(submit_clip(c1, "reel_king", "YouTube Shorts",
                         "https://youtube.com/shorts/demo102", 12800))
    s.append(submit_clip(c2, "clip_queen", "Instagram Reels",
                         "https://instagram.com/reel/demo103", 96500))
    s.append(submit_clip(c2, "viral_vibes", "TikTok",
                         "https://tiktok.com/@demo/video/104", 3100))
    s.append(submit_clip(c3, "reel_king", "YouTube Shorts",
                         "https://youtube.com/shorts/demo105", 8700))
    review_submission(s[0], 44800, approve=True)    # 44.8 * 1.5 = 67.20
    review_submission(s[1], 12100, approve=True)    # 12.1 * 1.5 = 18.15
    review_submission(s[2], 95000, approve=True)    # 95 * 2.0 = 190.00
    review_submission(s[3], 3100, approve=True)     # 3.1 * 2.0 = 6.20
    # s[4] stays pending on purpose — shows the review queue working
    return [c1, c2, c3]


def reset_all():
    with _db() as conn:
        conn.execute("DELETE FROM submissions")
        conn.execute("DELETE FROM campaigns")
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN "
                     "('campaigns','submissions')")
