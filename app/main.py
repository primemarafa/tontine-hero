from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from datetime import datetime

from app.database import init_db, get_db
from app.models import (
    get_profile,
    get_all_tontines,
    get_all_transactions,
    get_all_goals,
    calculate_health_score,
    format_currency,
    format_date_fr,
)


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    yield

app = FastAPI(title="Tontine Hero", lifespan=lifespan)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates.env.filters["currency"] = format_currency
templates.env.filters["date_fr"] = format_date_fr


# --- GET Routes ---

@app.get("/", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    profile = get_profile()
    tontines = get_all_tontines()
    transactions = get_all_transactions()
    goals = get_all_goals()
    health_score = calculate_health_score(profile, tontines, goals)

    next_payment = None
    next_payout = None

    for t in tontines:
        idx = t.get("current_cycle_index", 0)
        if idx < len(t.get("cycles", [])):
            curr_c = t["cycles"][idx]
            my_m = next((m for m in t.get("members", []) if m["is_current_user"] == 1), None)
            if my_m:
                pmt = curr_c["payments"].get(my_m["id"])
                if not pmt or not pmt.get("paid"):
                    if not next_payment or curr_c["due_date"] < next_payment["due_date"]:
                        next_payment = {
                            "tontine_name": t["name"],
                            "amount": t["contribution_amount"],
                            "due_date": curr_c["due_date"],
                        }

        my_m = next((m for m in t.get("members", []) if m["is_current_user"] == 1), None)
        if my_m:
            my_cycle = next((c for c in t.get("cycles", []) if c["beneficiary_id"] == my_m["id"] and c["status"] != "completed"), None)
            if my_cycle:
                if not next_payout or my_cycle["due_date"] < next_payout["due_date"]:
                    next_payout = {
                        "tontine_name": t["name"],
                        "amount": my_cycle["target_amount"],
                        "due_date": my_cycle["due_date"],
                        "round": my_cycle["round_number"],
                    }

    days_left = max(1, 30 - datetime.now().day)
    safe_daily = max(0, int(profile["balance"] / days_left))
    total_savings = sum(g["current_amount"] for g in goals)

    context = {
        "request": request,
        "active_tab": "dashboard",
        "profile": profile,
        "tontines": tontines,
        "transactions": transactions[:6],
        "goals": goals[:3],
        "health_score": health_score,
        "next_payment": next_payment,
        "next_payout": next_payout,
        "safe_daily": safe_daily,
        "total_savings": total_savings,
        "today_str": datetime.now().strftime("%Y-%m-%d"),
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)


@app.get("/tontines", response_class=HTMLResponse)
async def tontines_view(request: Request):
    profile = get_profile()
    tontines = get_all_tontines()
    goals = get_all_goals()
    health_score = calculate_health_score(profile, tontines, goals)

    context = {
        "request": request,
        "active_tab": "tontines",
        "profile": profile,
        "tontines": tontines,
        "health_score": health_score,
        "today_str": datetime.now().strftime("%Y-%m-%d"),
    }
    return templates.TemplateResponse(request=request, name="tontines.html", context=context)


@app.get("/budget", response_class=HTMLResponse)
async def budget_view(request: Request):
    profile = get_profile()
    tontines = get_all_tontines()
    transactions = get_all_transactions()
    goals = get_all_goals()
    health_score = calculate_health_score(profile, tontines, goals)

    total_income = sum(t["amount"] for t in transactions if t["type"] in ["income", "tontine_payout"])
    total_expense = sum(t["amount"] for t in transactions if t["type"] in ["expense", "tontine_payment", "savings_deposit"])
    tontine_contributions = sum(t["amount"] for t in transactions if t["type"] == "tontine_payment")

    categories = {}
    for t in transactions:
        if t["type"] in ["expense", "tontine_payment", "savings_deposit"]:
            cat = t["category"]
            categories[cat] = categories.get(cat, 0) + t["amount"]

    context = {
        "request": request,
        "active_tab": "budget",
        "profile": profile,
        "transactions": transactions,
        "total_income": total_income,
        "total_expense": total_expense,
        "tontine_contributions": tontine_contributions,
        "categories": categories,
        "health_score": health_score,
        "today_str": datetime.now().strftime("%Y-%m-%d"),
    }
    return templates.TemplateResponse(request=request, name="budget.html", context=context)


@app.get("/savings", response_class=HTMLResponse)
async def savings_view(request: Request):
    profile = get_profile()
    tontines = get_all_tontines()
    goals = get_all_goals()
    health_score = calculate_health_score(profile, tontines, goals)

    total_saved = sum(g["current_amount"] for g in goals)
    total_target = sum(g["target_amount"] for g in goals)
    global_percent = int((total_saved / total_target * 100)) if total_target > 0 else 0

    context = {
        "request": request,
        "active_tab": "savings",
        "profile": profile,
        "goals": goals,
        "total_saved": total_saved,
        "total_target": total_target,
        "global_percent": global_percent,
        "health_score": health_score,
    }
    return templates.TemplateResponse(request=request, name="savings.html", context=context)


@app.get("/simulator", response_class=HTMLResponse)
async def simulator_view(request: Request):
    profile = get_profile()
    tontines = get_all_tontines()
    goals = get_all_goals()
    health_score = calculate_health_score(profile, tontines, goals)

    context = {
        "request": request,
        "active_tab": "simulator",
        "profile": profile,
        "health_score": health_score,
    }
    return templates.TemplateResponse(request=request, name="simulator.html", context=context)


# --- POST Routes ---

@app.post("/api/transactions")
async def add_transaction(
    type: str = Form(...),
    category: str = Form(...),
    amount: float = Form(..., gt=0),
    date: str = Form(...),
    description: str = Form(""),
    redirect_to: str = Form("/")
):
    with get_db() as conn:
        cursor = conn.cursor()
        tx_id = f"tx-{int(datetime.now().timestamp() * 1000)}"
        desc = description.strip() or category

        cursor.execute("""
            INSERT INTO transactions (id, type, category, amount, date, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tx_id, type, category, amount, date, desc))

        balance_change = amount if type in ["income", "tontine_payout"] else -amount
        cursor.execute("UPDATE profile SET balance = balance + ? WHERE id = 1", (balance_change,))

        conn.commit()
    return RedirectResponse(url=redirect_to, status_code=303)


@app.post("/api/goals")
async def add_goal(
    title: str = Form(...),
    target_amount: float = Form(..., gt=0),
    current_amount: float = Form(0.0, ge=0),
    category: str = Form("equipement"),
    target_date: str = Form(None),
    icon: str = Form("--")
):
    colors = {
        "equipement": "from-blue-500",
        "urgence": "from-emerald-500",
        "formation": "from-amber-500",
        "business": "from-purple-500",
        "famille": "from-rose-500",
    }
    color = colors.get(category, "from-slate-600")

    with get_db() as conn:
        cursor = conn.cursor()
        goal_id = f"goal-{int(datetime.now().timestamp() * 1000)}"

        cursor.execute("""
            INSERT INTO savings_goals (id, title, target_amount, current_amount, category, target_date, icon, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (goal_id, title.strip(), target_amount, current_amount, category, target_date or None, icon, color))

        conn.commit()
    return RedirectResponse(url="/savings", status_code=303)


@app.post("/api/goals/{goal_id}/deposit")
async def deposit_goal(goal_id: str, amount: float = Form(..., gt=0), redirect_to: str = Form("/savings")):
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM savings_goals WHERE id = ?", (goal_id,))
        goal = cursor.fetchone()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        cursor.execute("UPDATE savings_goals SET current_amount = current_amount + ? WHERE id = ?", (amount, goal_id))
        cursor.execute("UPDATE profile SET balance = balance - ? WHERE id = 1", (amount,))

        tx_id = f"tx-{int(datetime.now().timestamp() * 1000)}"
        cursor.execute("""
            INSERT INTO transactions (id, type, category, amount, date, description, related_goal_id)
            VALUES (?, 'savings_deposit', 'Epargne Projet', ?, ?, ?, ?)
        """, (tx_id, amount, datetime.now().strftime("%Y-%m-%d"), f"Versement tirelire - {goal['title']}", goal_id))

        conn.commit()
    return RedirectResponse(url=redirect_to, status_code=303)


@app.post("/api/tontines/payment")
async def toggle_tontine_payment(
    cycle_id: str = Form(...),
    member_id: str = Form(...),
    paid: int = Form(...),
    tontine_id: str = Form(...),
    redirect_to: str = Form("/tontines")
):
    with get_db() as conn:
        cursor = conn.cursor()

        paid_at = datetime.now().strftime("%Y-%m-%d") if paid == 1 else None
        cursor.execute("""
            UPDATE tontine_payments
            SET paid = ?, paid_at = ?, method = 'Wave'
            WHERE cycle_id = ? AND member_id = ?
        """, (paid, paid_at, cycle_id, member_id))

        cursor.execute("SELECT SUM(amount) as total FROM tontine_payments WHERE cycle_id = ? AND paid = 1", (cycle_id,))
        row = cursor.fetchone()
        total_collected = row["total"] if row and row["total"] else 0.0

        cursor.execute("UPDATE tontine_cycles SET total_collected = ? WHERE id = ?", (total_collected, cycle_id))

        conn.commit()
    return RedirectResponse(url=redirect_to, status_code=303)


@app.post("/api/tontines/{tontine_id}/advance")
async def advance_tontine_cycle(tontine_id: str, redirect_to: str = Form("/tontines")):
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tontines WHERE id = ?", (tontine_id,))
        tontine = cursor.fetchone()
        if not tontine:
            raise HTTPException(status_code=404, detail="Tontine not found")

        curr_idx = tontine["current_cycle_index"]
        cursor.execute("SELECT * FROM tontine_cycles WHERE tontine_id = ? ORDER BY round_number ASC", (tontine_id,))
        cycles = cursor.fetchall()

        if curr_idx < len(cycles) - 1:
            next_idx = curr_idx + 1
            cursor.execute("UPDATE tontine_cycles SET status = 'completed' WHERE id = ?", (cycles[curr_idx]["id"],))
            cursor.execute("UPDATE tontine_cycles SET status = 'current' WHERE id = ?", (cycles[next_idx]["id"],))
            cursor.execute("UPDATE tontines SET current_cycle_index = ? WHERE id = ?", (next_idx, tontine_id))

        conn.commit()
    return RedirectResponse(url=redirect_to, status_code=303)


@app.post("/api/profile/currency")
async def change_currency(currency: str = Form(...), redirect_to: str = Form("/")):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE profile SET currency = ? WHERE id = 1", (currency,))
        conn.commit()
    return RedirectResponse(url=redirect_to, status_code=303)
