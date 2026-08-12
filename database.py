


"""
database.py
-----------
Handles all SQLite operations: users + scan history.

Run directly to inspect the database:
    python database.py
"""

import sqlite3
import hashlib
import os

# Always store the DB next to this file, regardless of where Flask is launched from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "agroscan.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()

    # ── Create tables ─────────────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name  TEXT NOT NULL,
            email      TEXT NOT NULL UNIQUE,
            phone      TEXT,
            location   TEXT,
            password   TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            plant       TEXT NOT NULL,
            disease     TEXT NOT NULL,
            status      TEXT NOT NULL,
            confidence  REAL NOT NULL,
            scanned_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Migration: add user_id to old DBs that were created without it ────
    scan_cols = [r[1] for r in conn.execute("PRAGMA table_info(scans)").fetchall()]
    if "user_id" not in scan_cols:
        conn.execute("ALTER TABLE scans ADD COLUMN user_id INTEGER")
        print("[DB] Migrated: added user_id column to scans table.")

    conn.commit()
    conn.close()


# ── User helpers ──────────────────────────────────────────────────────────────
def register_user(full_name, email, phone, location, password):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (full_name, email, phone, location, password) VALUES (?,?,?,?,?)",
            (full_name, email, phone, location, hash_password(password)),
        )
        conn.commit()
        return True, "Registered successfully"
    except sqlite3.IntegrityError:
        return False, "Email already registered"
    finally:
        conn.close()


def login_user(email, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(user_id, full_name, phone, location):
    """Update non-sensitive profile fields."""
    conn = get_connection()
    conn.execute(
        "UPDATE users SET full_name=?, phone=?, location=? WHERE id=?",
        (full_name, phone, location, user_id),
    )
    conn.commit()
    conn.close()


def change_password(user_id, old_password, new_password):
    """Change password after verifying the old one. Returns (ok, message)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM users WHERE id=? AND password=?",
        (user_id, hash_password(old_password)),
    ).fetchone()
    if not row:
        conn.close()
        return False, "Current password is incorrect"
    conn.execute(
        "UPDATE users SET password=? WHERE id=?",
        (hash_password(new_password), user_id),
    )
    conn.commit()
    conn.close()
    return True, "Password updated successfully"


# ── Scan helpers ──────────────────────────────────────────────────────────────
def save_scan(user_id, plant, disease, status, confidence):
    conn = get_connection()
    conn.execute(
        "INSERT INTO scans (user_id, plant, disease, status, confidence) VALUES (?,?,?,?,?)",
        (user_id, plant, disease, status, round(confidence, 4)),
    )
    conn.commit()
    conn.close()


def get_user_scans(user_id, limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM scans WHERE user_id=? ORDER BY scanned_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_stats(user_id):
    conn = get_connection()
    total    = conn.execute("SELECT COUNT(*) FROM scans WHERE user_id=?",                          (user_id,)).fetchone()[0]
    healthy  = conn.execute("SELECT COUNT(*) FROM scans WHERE user_id=? AND status='Healthy'",    (user_id,)).fetchone()[0]
    diseased = conn.execute("SELECT COUNT(*) FROM scans WHERE user_id=? AND status='Diseased'",   (user_id,)).fetchone()[0]
    conn.close()
    return {"total": total, "healthy": healthy, "diseased": diseased}


# ── CLI inspector ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    conn = get_connection()

    print(f"\n📂 Database path: {DB_PATH}\n")

    # Users
    users = conn.execute(
        "SELECT id, full_name, email, phone, location, created_at FROM users"
    ).fetchall()
    print(f"👤 USERS  ({len(users)} total)")
    print("─" * 72)
    for u in users:
        print(f"  [{u['id']}] {u['full_name']:<20} {u['email']:<30} "
              f"{u['phone'] or '—':>12}  📍{u['location'] or '—'}  joined {u['created_at'][:10]}")

    print()

    # Scans (joined with user name)
    scans = conn.execute("""
        SELECT s.id, COALESCE(u.full_name,'(deleted)') AS name,
               s.plant, s.disease, s.status, s.confidence, s.scanned_at
        FROM   scans s
        LEFT JOIN users u ON s.user_id = u.id
        ORDER  BY s.scanned_at DESC
        LIMIT  20
    """).fetchall()
    print(f"🔍 RECENT SCANS  ({len(scans)} shown, max 20)")
    print("─" * 72)
    for s in scans:
        icon = "✅" if s['status'] == 'Healthy' else "⚠️"
        print(f"  [{s['id']}] {icon}  {s['plant']:<14} {s['disease']:<30} "
              f"{s['confidence']:>6.2f}%  by {s['name']}  {s['scanned_at'][:16]}")

    conn.close()
    print()
