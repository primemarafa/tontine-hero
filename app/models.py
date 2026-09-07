from datetime import datetime
import urllib.parse
from app.database import get_db


def format_currency(amount: float, currency: str = "XOF") -> str:
    rounded = int(round(amount))
    formatted = f"{rounded:,}".replace(",", " ")
    if currency in ["XOF", "XAF"]:
        return f"{formatted} FCFA"
    elif currency == "EUR":
        return f"{formatted} EUR"
    elif currency == "USD":
        return f"${formatted}"
    elif currency == "GNF":
        return f"{formatted} GNF"
    return f"{formatted} {currency}"


def format_date_fr(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
        months = ["janv.", "fevr.", "mars", "avr.", "mai", "juin",
                   "juil.", "aout", "sept.", "oct.", "nov.", "dec."]
        return f"{dt.day} {months[dt.month - 1]} {dt.year}"
    except Exception:
        return date_str


def get_profile():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profile WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
    return {
        "name": "Moustapha",
        "avatar": "MO",
        "currency": "XOF",
        "balance": 385000,
        "monthly_income": 650000,
        "streak_days": 8,
    }


def get_all_tontines():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tontines ORDER BY id ASC")
        tontine_rows = cursor.fetchall()

        tontines = []
        for t_row in tontine_rows:
            t = dict(t_row)
            t_id = t["id"]

            cursor.execute("SELECT * FROM tontine_members WHERE tontine_id = ? ORDER BY payout_rank ASC", (t_id,))
            members = [dict(m) for m in cursor.fetchall()]
            t["members"] = members

            cursor.execute("SELECT * FROM tontine_cycles WHERE tontine_id = ? ORDER BY round_number ASC", (t_id,))
            cycle_rows = cursor.fetchall()
            cycles = []
            for c_row in cycle_rows:
                c = dict(c_row)
                c_id = c["id"]

                cursor.execute("SELECT * FROM tontine_payments WHERE cycle_id = ?", (c_id,))
                payments = {p["member_id"]: dict(p) for p in cursor.fetchall()}
                c["payments"] = payments

                beneficiary = next((m for m in members if m["id"] == c["beneficiary_id"]), None)
                c["beneficiary"] = beneficiary

                cycles.append(c)

            t["cycles"] = cycles
            tontines.append(t)

    return tontines


def get_all_transactions():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC")
        txs = [dict(row) for row in cursor.fetchall()]
    return txs


def get_all_goals():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM savings_goals ORDER BY target_amount DESC")
        goals = [dict(row) for row in cursor.fetchall()]
    return goals


def calculate_health_score(profile, tontines, goals):
    score = 50
    tips = []

    if profile.get("streak_days", 0) >= 7:
        score += 10
    else:
        tips.append("Ouvre l'application chaque jour pour maintenir ta regularite.")

    total_saved = sum(g["current_amount"] for g in goals)
    total_target = sum(g["target_amount"] for g in goals)
    if total_target > 0:
        ratio = total_saved / total_target
        score += min(20, int(ratio * 20))
    else:
        tips.append("Cree au moins un objectif d'epargne ou un fonds de securite.")

    if profile.get("balance", 0) > 0:
        score += 15
    else:
        score -= 20
        tips.append("Attention : ton solde disponible est tres bas.")

    overdue = 0
    for t in tontines:
        idx = t.get("current_cycle_index", 0)
        if idx < len(t.get("cycles", [])):
            curr_c = t["cycles"][idx]
            my_m = next((m for m in t.get("members", []) if m["is_current_user"] == 1), None)
            if my_m:
                pmt = curr_c["payments"].get(my_m["id"])
                if not pmt or not pmt.get("paid"):
                    overdue += 1

    if overdue == 0:
        score += 15
    else:
        score -= 15
        tips.append("Tu as au moins une cotisation de tontine en attente.")

    final_score = max(10, min(100, score))
    label = "Serenite Totale" if final_score >= 80 else ("Bien Gere" if final_score >= 60 else "Vigilance")
    level = "Excellent" if final_score >= 80 else ("En bonne voie" if final_score >= 60 else "A surveiller")

    return {"score": final_score, "level": level, "label": label, "tips": tips}
