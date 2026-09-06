import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tontine.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        avatar TEXT NOT NULL,
        currency TEXT NOT NULL DEFAULT 'XOF',
        balance REAL NOT NULL,
        monthly_income REAL NOT NULL,
        streak_days INTEGER NOT NULL,
        last_active_date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tontines (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        contribution_amount REAL NOT NULL,
        currency TEXT NOT NULL,
        frequency TEXT NOT NULL,
        start_date TEXT NOT NULL,
        role TEXT NOT NULL,
        current_cycle_index INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'active'
    );

    CREATE TABLE IF NOT EXISTS tontine_members (
        id TEXT PRIMARY KEY,
        tontine_id TEXT NOT NULL,
        name TEXT NOT NULL,
        avatar TEXT NOT NULL,
        phone TEXT,
        is_current_user INTEGER NOT NULL DEFAULT 0,
        reliability_score INTEGER NOT NULL DEFAULT 100,
        payout_rank INTEGER NOT NULL,
        FOREIGN KEY (tontine_id) REFERENCES tontines(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tontine_cycles (
        id TEXT PRIMARY KEY,
        tontine_id TEXT NOT NULL,
        round_number INTEGER NOT NULL,
        due_date TEXT NOT NULL,
        beneficiary_id TEXT NOT NULL,
        total_collected REAL NOT NULL DEFAULT 0,
        target_amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'upcoming',
        FOREIGN KEY (tontine_id) REFERENCES tontines(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tontine_payments (
        cycle_id TEXT NOT NULL,
        member_id TEXT NOT NULL,
        paid INTEGER NOT NULL DEFAULT 0,
        paid_at TEXT,
        amount REAL NOT NULL,
        method TEXT DEFAULT 'Wave',
        PRIMARY KEY (cycle_id, member_id),
        FOREIGN KEY (cycle_id) REFERENCES tontine_cycles(id) ON DELETE CASCADE,
        FOREIGN KEY (member_id) REFERENCES tontine_members(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        related_tontine_id TEXT,
        related_goal_id TEXT
    );

    CREATE TABLE IF NOT EXISTS savings_goals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL NOT NULL,
        category TEXT NOT NULL,
        target_date TEXT,
        icon TEXT NOT NULL,
        color TEXT NOT NULL
    );
    """)

    # Check if data exists; if not, seed realistic data
    cursor.execute("SELECT COUNT(*) as count FROM profile")
    if cursor.fetchone()["count"] == 0:
        seed_initial_data(conn)

    conn.commit()
    conn.close()

def seed_initial_data(conn):
    cursor = conn.cursor()
    
    # 1. Profile
    cursor.execute("""
        INSERT INTO profile (id, name, avatar, currency, balance, monthly_income, streak_days, last_active_date)
        VALUES (1, 'Moustapha', '👨🏾‍💻', 'XOF', 385000, 650000, 8, ?)
    """, (datetime.now().isoformat(),))

    # 2. Tontine 1
    t1_id = "tontine-1"
    cursor.execute("""
        INSERT INTO tontines (id, name, description, contribution_amount, currency, frequency, start_date, role, current_cycle_index, status)
        VALUES (?, 'Tontine Frères & Proches', 'Cotisation mensuelle pour financer nos projets et investissements respectifs.', 50000, 'XOF', 'monthly', '2026-07-01', 'organizer', 2, 'active')
    """, (t1_id,))

    members_t1 = [
        ("m-1", t1_id, "Moustapha (Moi)", "👨🏾‍💻", "+221770000001", 1, 100, 3),
        ("m-2", t1_id, "Ibrahim Diop", "👨🏾", "+221770000002", 0, 95, 1),
        ("m-3", t1_id, "Fatou Ndiaye", "👩🏾", "+221770000003", 0, 100, 2),
        ("m-4", t1_id, "Amadou Sow", "🧔🏾", "+221770000004", 0, 90, 4),
        ("m-5", t1_id, "Aïssatou Ba", "🧕🏾", "+221770000005", 0, 100, 5),
    ]
    cursor.executemany("""
        INSERT INTO tontine_members (id, tontine_id, name, avatar, phone, is_current_user, reliability_score, payout_rank)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, members_t1)

    cycles_t1 = [
        ("c-1", t1_id, 1, "2026-07-05", "m-2", 250000, 250000, "completed"),
        ("c-2", t1_id, 2, "2026-08-05", "m-3", 250000, 250000, "completed"),
        ("c-3", t1_id, 3, "2026-09-05", "m-1", 200000, 250000, "current"),
        ("c-4", t1_id, 4, "2026-10-05", "m-4", 0, 250000, "upcoming"),
        ("c-5", t1_id, 5, "2026-11-05", "m-5", 0, 250000, "upcoming"),
    ]
    cursor.executemany("""
        INSERT INTO tontine_cycles (id, tontine_id, round_number, due_date, beneficiary_id, total_collected, target_amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, cycles_t1)

    payments_t1 = [
        # Cycle 1 (completed)
        ("c-1", "m-1", 1, "2026-07-04", 50000, "Wave"),
        ("c-1", "m-2", 1, "2026-07-05", 50000, "Espèces"),
        ("c-1", "m-3", 1, "2026-07-05", 50000, "Orange Money"),
        ("c-1", "m-4", 1, "2026-07-06", 50000, "Wave"),
        ("c-1", "m-5", 1, "2026-07-04", 50000, "Wave"),
        # Cycle 2 (completed)
        ("c-2", "m-1", 1, "2026-08-03", 50000, "Wave"),
        ("c-2", "m-2", 1, "2026-08-05", 50000, "Orange Money"),
        ("c-2", "m-3", 1, "2026-08-05", 50000, "Espèces"),
        ("c-2", "m-4", 1, "2026-08-05", 50000, "Wave"),
        ("c-2", "m-5", 1, "2026-08-04", 50000, "Orange Money"),
        # Cycle 3 (current - tour de Moustapha !)
        ("c-3", "m-1", 1, "2026-09-01", 50000, "Wave"),
        ("c-3", "m-2", 1, "2026-09-02", 50000, "Orange Money"),
        ("c-3", "m-3", 1, "2026-09-02", 50000, "Wave"),
        ("c-3", "m-4", 0, None, 50000, None),
        ("c-3", "m-5", 1, "2026-09-03", 50000, "Wave"),
        # Cycle 4 (upcoming)
        ("c-4", "m-1", 0, None, 50000, None),
        ("c-4", "m-2", 0, None, 50000, None),
        ("c-4", "m-3", 0, None, 50000, None),
        ("c-4", "m-4", 0, None, 50000, None),
        ("c-4", "m-5", 0, None, 50000, None),
        # Cycle 5 (upcoming)
        ("c-5", "m-1", 0, None, 50000, None),
        ("c-5", "m-2", 0, None, 50000, None),
        ("c-5", "m-3", 0, None, 50000, None),
        ("c-5", "m-4", 0, None, 50000, None),
        ("c-5", "m-5", 0, None, 50000, None),
    ]
    cursor.executemany("""
        INSERT INTO tontine_payments (cycle_id, member_id, paid, paid_at, amount, method)
        VALUES (?, ?, ?, ?, ?, ?)
    """, payments_t1)

    # 3. Transactions
    txs = [
        ("tx-1", "income", "Salaire / Mission", 450000, "2026-09-01", "Paiement contrat client dev web", None, None),
        ("tx-2", "tontine_payment", "Cotisation Tontine", 50000, "2026-09-01", "Cotisation Tour 3 — Tontine Frères & Proches", t1_id, None),
        ("tx-3", "expense", "Alimentation & Courses", 40000, "2026-09-02", "Courses supermarché & marché", None, None),
        ("tx-4", "savings_deposit", "Épargne Projet", 35000, "2026-09-02", "Ajout tirelire PC Travail", None, "goal-1"),
        ("tx-5", "expense", "Transport & Carburant", 15000, "2026-09-03", "Recharge carte transport / carburant", None, None),
    ]
    cursor.executemany("""
        INSERT INTO transactions (id, type, category, amount, date, description, related_tontine_id, related_goal_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, txs)

    # 4. Goals
    goals = [
        ("goal-1", "Matériel PC / Setup Travail", 500000, 320000, "equipement", "2026-11-30", "💻", "from-blue-500 to-indigo-600"),
        ("goal-2", "Fonds de Sécurité & Urgences", 300000, 180000, "urgence", "2026-12-31", "🛡️", "from-emerald-500 to-teal-600"),
        ("goal-3", "Financement Formation & Certifs", 150000, 65000, "formation", "2026-10-15", "🎓", "from-amber-500 to-orange-600"),
    ]
    cursor.executemany("""
        INSERT INTO savings_goals (id, title, target_amount, current_amount, category, target_date, icon, color)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, goals)
