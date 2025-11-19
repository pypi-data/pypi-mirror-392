import requests
import json
import logging
from datetime import datetime
from baltra_sdk.legacy.dashboards_folder.models import Employees, Rewards, db
from datetime import datetime, timedelta, date
from sqlalchemy import func
from app.images.report_generator import generate_MTWA_charts
from baltra_sdk.shared.utils.batch.chart_generator_old import generate_charts
from baltra_sdk.shared.utils.batch.calculate_points import run_test
from flask import current_app


def login():
    #Load credentials for API Calls
    API_URL = current_app.config["API_URL_MTWA"]
    USERNAME = current_app.config["USERNAME_MTWA"]
    PASSWORD = current_app.config["PASSWORD_MTWA"]
    payload = {
        "action": "login",
        "parameters": {
            "login_name": USERNAME,
            "password": PASSWORD
        }
    }

    response = requests.post(API_URL, data={"json": json.dumps(payload)})
    data = response.json()

    if data.get("result") == "ok":
        return data["session_token"]
    else:
        raise Exception(f"Login failed: {data.get('message')}")

def call_api(action, token, parameters=None):
    API_URL = current_app.config["API_URL_MTWA"]
    payload = {
        "action": action,
        "session_token": token,
        "parameters": parameters or {}
    }
    
    response = requests.post(API_URL, data={"json": json.dumps(payload)})
    return response.json()

def parse_date(raw_date):
    if not raw_date:
        return None
    try:
        return datetime.strptime(raw_date, "%Y-%m-%d").date()
    except Exception as e:
        logging.warning(f"Invalid date format: {raw_date} - {e}")
        return None

def clean_wa_id(wa_id):
    wa_id = str(wa_id or "").strip()
    if len(wa_id) == 13 and wa_id.isdigit():
        return wa_id
    logging.info(f'Unaccepted format for wa_id {wa_id}')
    return None

def parse_score(att_type):
    if att_type == "ASISTENCIA":
        return "1"
    elif att_type == "FALTA":
        return "0"
    else:
        return "n/a"

def get_date_intervals():
    today = datetime.today().date()

    # Employees: from 1 month ago to today
    employees_start = date(2000, 1, 1)

    employees_end = today

    # Attendance: from today to latest attendance date in rewards for company_id=10
    latest_attendance = db.session.query(func.max(Rewards.date)).filter(
        Rewards.metric == "attendance",
        Rewards.company_id == 10
    ).scalar()
    if not latest_attendance:
        # fallback if no data found
        latest_attendance = today
    attendance_start = latest_attendance
    attendance_end = today

    # Training: first to last day of previous month
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    training_start = last_day_prev_month.replace(day=1)
    training_end = last_day_prev_month

    return {
        "employees": {"start_date": employees_start.isoformat(), "end_date": employees_end.isoformat()},
        "attendance": {"start_date": attendance_start.isoformat(), "end_date": attendance_end.isoformat()},
        "training": {"start_date": training_start.isoformat(), "end_date": training_end.isoformat()},
    }

def sync_employees_from_api(api_data):
    api_employees = api_data.get("employees", [])
    COMPANY_ID = 10

    existing = {
        str(e.customer_key).strip(): e
        for e in Employees.query.filter_by(company_id=COMPANY_ID).all()
    }
    api_keys = set()

    inserted = 0
    updated = 0

    for emp_data in api_employees:
        customer_key = str(emp_data.get("customer_key", "")).strip()
        if not customer_key or customer_key == "7582":
            logging.info(f'Ignored Dummy employee 7582')
            continue  # Skip dummy

        role_raw = (emp_data.get("role", "") or "").strip().upper()
        if role_raw == "JEFE DE OPERACIONES":
            logging.info("Ignored JEFE DE OPERACIONES")
            continue  # Skip this role

        # Normalize 'OPERADOR 5' to 'OPERADOR'
        normalized_role = "OPERADOR" if role_raw == "OPERADOR 5" else emp_data.get("role", "").strip()

        api_keys.add(customer_key)
        first_name = (emp_data.get("first_name", "") or "").strip()
        last_name = (emp_data.get("last_name", "") or "").strip()
        wa_id = clean_wa_id(emp_data.get("wa_id"))

        start_date = parse_date(emp_data.get("start_date"))
        end_date_raw = emp_data.get("end_date")
        end_date = parse_date(end_date_raw) if end_date_raw else None

        if customer_key in existing:
            emp = existing[customer_key]
            emp.first_name = first_name
            emp.last_name = last_name
            if wa_id:  # Only update if wa_id is not empty or None
                emp.wa_id = wa_id
            emp.area = (emp_data.get("sub_area", "") or "").strip()
            emp.sub_area = normalized_role
            emp.role = normalized_role
            emp.shift = (emp_data.get("shift", "") or "").strip()
            emp.start_date = start_date
            emp.end_date = end_date
            emp.birth_date = parse_date(emp_data.get("birth_date"))
            emp.left_company = bool(end_date)
            emp.active = not emp.left_company
            emp.company_id = COMPANY_ID
            updated += 1
        else:
            emp = Employees(
                first_name=first_name,
                last_name=last_name,
                wa_id=wa_id,
                area=(emp_data.get("sub_area", "").strip() or ""),
                sub_area=normalized_role,
                role=normalized_role,
                shift=(emp_data.get("shift", "").strip() or ""),
                start_date=start_date,
                end_date=end_date,
                birth_date=parse_date(emp_data.get("birth_date")),
                customer_key=customer_key,
                left_company=bool(end_date),
                active=not bool(end_date),
                company_id=COMPANY_ID
            )
            db.session.add(emp)
            inserted += 1

    db.session.commit()
    logging.info(f"🟢 Sync Complete: {inserted} inserted, {updated} updated.")


def sync_attendance_from_api(api_data):
    api_attendance = api_data.get("Attendancelist", [])
    COMPANY_ID = 10

    logging.info(f'🟡 Attendance List: {len(api_attendance)} records received.')

    # Build set of customer_keys in the API data
    customer_keys = set(str(r.get("employee")) for r in api_attendance if r.get("employee"))

    # Get all relevant employees
    employees = Employees.query.filter(
        Employees.company_id == COMPANY_ID,
        Employees.customer_key.in_(customer_keys)
    ).all()

    employees_map = {e.customer_key: e for e in employees}
    employee_ids = [e.employee_id for e in employees]

    # Get all relevant dates
    all_dates = list(set(r.get("date") for r in api_attendance if r.get("date")))

    # Fetch existing rewards to prevent duplicates
    existing_rewards = Rewards.query.filter(
        Rewards.company_id == COMPANY_ID,
        Rewards.employee_id.in_(employee_ids),
        Rewards.date.in_(all_dates),
        Rewards.metric.in_(["attendance", "punctuality"])
    ).all()

    existing_keys = set(
        (r.employee_id, r.date, r.metric)
        for r in existing_rewards
    )

    rewards_to_insert = []
    duplicates_skipped = 0

    for record in api_attendance:
        customer_key = str(record.get("employee"))
        date_str = record.get("date")
        att_type = record.get("type", "").strip().upper()

        if not customer_key or not date_str or not att_type:
            continue

        employee = employees_map.get(customer_key)
        if not employee:
            logging.warning(f"⚠️ Employee with customer_key {customer_key} not found.")
            continue

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            logging.error(f"❌ Invalid date format: {date_str}")
            continue

        week_number = date_obj.isocalendar()[1]
        weekday = date_obj.isoweekday()
        score = parse_score(att_type)

        for metric in ["attendance", "punctuality"]:
            key = (employee.employee_id, date_obj, metric)
            if key in existing_keys:
                duplicates_skipped += 1
                continue

            reward = Rewards(
                employee_id=employee.employee_id,
                customer_key=employee.customer_key,
                company_id=COMPANY_ID,
                date=date_obj,
                week=week_number,
                weekday=weekday,
                metric=metric,
                score=score
            )
            rewards_to_insert.append(reward)

    if rewards_to_insert:
        db.session.bulk_save_objects(rewards_to_insert)
        db.session.commit()
        logging.info(f"🟢 Rewards sync complete: {len(rewards_to_insert)} records inserted.")
    else:
        logging.info("🟡 No new rewards to insert — all records were duplicates.")

    logging.info(f"🧾 Duplicate reward entries skipped: {duplicates_skipped}")

def sync_training_from_api(api_data, save_date):
    logging.info(f'Api Response Training: {api_data}')
    api_training = api_data.get("coursesPerEmployee", [])
    COMPANY_ID = 10

    fixed_date = datetime.strptime(save_date, "%Y-%m-%d").date()
    week_number = fixed_date.isocalendar()[1]
    weekday = fixed_date.isoweekday()

    logging.info(f"🟡 Training data: {len(api_training)} employee records")

    # Build set of customer_keys from API
    customer_keys = set(str(rec.get("employee")) for rec in api_training if rec.get("employee"))

    # Get employees for those customer_keys
    employees = Employees.query.filter(
        Employees.company_id == COMPANY_ID,
        Employees.customer_key.in_(customer_keys)
    ).all()
    employees_map = {e.customer_key: e for e in employees}
    employee_ids = [e.employee_id for e in employees]

    # Fetch existing rewards for this fixed date & these employees & metrics to avoid duplicates
    existing_rewards = Rewards.query.filter(
        Rewards.company_id == COMPANY_ID,
        Rewards.employee_id.in_(employee_ids),
        Rewards.date == fixed_date,
        Rewards.metric.in_(["assigned_courses", "completed_courses"])
    ).all()

    existing_keys = set(
        (r.employee_id, r.date, r.metric)
        for r in existing_rewards
    )

    rewards_to_insert = []
    duplicates_skipped = 0

    for rec in api_training:
        customer_key = str(rec.get("employee"))
        if not customer_key:
            continue

        employee = employees_map.get(customer_key)
        if not employee:
            logging.warning(f"⚠️ Employee with customer_key {customer_key} not found.")
            continue

        for metric in ["assigned_courses", "completed_courses"]:
            score_value = rec.get(metric)
            if score_value is None:
                continue  # no data for this metric

            key = (employee.employee_id, fixed_date, metric)
            if key in existing_keys:
                duplicates_skipped += 1
                continue

            reward = Rewards(
                employee_id=employee.employee_id,
                customer_key=employee.customer_key,
                company_id=COMPANY_ID,
                date=fixed_date,
                week=week_number,
                weekday=weekday,
                metric=metric,
                score=str(score_value)  # store as string to match your schema
            )
            rewards_to_insert.append(reward)

    if rewards_to_insert:
        db.session.bulk_save_objects(rewards_to_insert)
        db.session.commit()
        logging.info(f"🟢 Training sync complete: {len(rewards_to_insert)} records inserted.")
    else:
        logging.info("🟡 No new training rewards to insert (all duplicates or empty).")

    logging.info(f"🧾 Duplicate training entries skipped: {duplicates_skipped}")

def test_MTWA(current_app):
    with current_app.app_context():
        intervals = get_date_intervals()

        session_token = login()

        # Employees sync
        api_response = call_api("getEmployeeDirectory", session_token, intervals["employees"])
        logging.info(f'Api Response: {api_response}')
        sync_employees_from_api(api_response)

        # Attendance sync
        api_response = call_api("getAttendanceList", session_token, intervals["attendance"])
        sync_attendance_from_api(api_response)

        # Training sync
        save_date = intervals["training"]["start_date"]
        api_response = call_api("getTrainingCompliance", session_token, intervals["training"])
        sync_training_from_api(api_response, save_date)

        #calculate points
        run_test(10, date.today().isocalendar()[1]-1, "weekly")
        #update charts new
        generate_MTWA_charts(10)
        #update charts prizes
        generate_charts(10)