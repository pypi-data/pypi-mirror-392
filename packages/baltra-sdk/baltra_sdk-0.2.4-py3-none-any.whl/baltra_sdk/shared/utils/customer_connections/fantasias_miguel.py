import pyodbc
from datetime import datetime, timedelta, date
import logging
from sqlalchemy import and_
from baltra_sdk.legacy.dashboards_folder.models import Employees, Rewards, Companies, db
from collections import defaultdict
import re
from app.images.report_generator import generate_fantasias_charts, generate_ranking_charts
from baltra_sdk.shared.utils.batch.calculate_points import run_test
from flask import current_app
import json
import tempfile
from openai import OpenAI
import os

def determine_sub_area(role: str, start_date: date, reference_date: date = None) -> str:
    """
    Classify into sub-areas based on role and tenure.
    Autoservicio / Mostrador / Mayoreo / Distribuidor / Operativos
    1 = 1-2 months (60%), 2 = 3-5 months (80%), 3 = 6+ months (100%)
    """
    if not role or role.strip() == "":
        return "No Atendido"

    if reference_date is None:
        reference_date = date.today()

    role = role.strip()
    tenure_months = months_between(start_date, reference_date)

    # Determine main area
    if "Distribuidor" in role:
        main_area = "Distribuidor"
    elif role == "Anfitrión de Mayoreo Sucursal":
        main_area = "Mayoreo"
    elif "Mostrador" in role:
        main_area = "Mostrador"
    elif "Autoservicio" in role:
        main_area = "Autoservicio"
    else:
        main_area = "Operativos"

    # Assign sub-area based on tenure
    if tenure_months < 2:
        sub_area_suffix = "1"  # 1-2 months -> 60%
    elif 2 <= tenure_months <= 5:
        sub_area_suffix = "2"  # 3-5 months -> 80%
    else:
        sub_area_suffix = "3"  # 6+ months -> 100%

    return f"{main_area} {sub_area_suffix}"

def months_between(start: date, end: date) -> int:
    """Return number of full months between two dates."""
    if not start or not end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)

def fetch_employees():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={current_app.config['SERVER_FANTASIAS']};"
        f"DATABASE=Baltra;"
        f"UID={current_app.config['UID_FANTASIAS']};"
        f"PWD={current_app.config['PWD_FANTASIAS']};"
        "TrustServerCertificate=yes;"
        "Encrypt=yes;"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Baltra_Bamboo;")
    columns = [column[0].strip() for column in cursor.description]
    rows = cursor.fetchall()

    employees = []
    for row in rows:
        row_data = dict(zip(columns, row))

        raw_cel = row_data.get("Celular") or ""
        celular = re.sub(r"\D", "", raw_cel)  # removes all non-digit characters
        if len(celular) == 10:
            wa_id = f"521{celular}"
        else:
            wa_id = None
            if raw_cel.strip():  # log only if non-empty original value
                logging.warning(f"Malformed celular: '{raw_cel}' for employee: {row_data.get('NombrePreferido', '').strip()} {row_data.get('Apellido', '').strip()}")

        tienda = (row_data.get("Tienda") or "").strip()
        area_map = {"T26": "Pedregal", "T13": "Lomas", "T18": "Santa Fe", "T23":"Coyoacan"}
        area = area_map.get(tienda, tienda)
        transformed = {
            "first_name": (row_data.get("NombrePreferido") or "").strip(),
            "last_name": (row_data.get("Apellido") or "").strip(),
            "wa_id": wa_id,
            "company_id": 9,
            "area": area,
            "role": (row_data.get("Puesto") or "").strip(),
            "context": None,
            "weekly_path": None,
            "daily_path": None,
            "monthly_path": None,
            "rewards_path": None,
            "active": True,
            "shift": "afternoon",
            "left_company": bool(row_data.get("FechaBaja")),
            "start_date": row_data.get("FechaIngreso"),
            "end_date": row_data.get("FechaBaja"),
            "customer_key": (row_data.get("No_Emp") or "").strip(),
            "birth_date": None,
            "sub_area": determine_sub_area(row_data.get("Puesto"), row_data.get("FechaIngreso")),
        }
        employees.append(transformed)

    cursor.close()
    conn.close()
    return employees

def upsert_employees(employees_data: list[dict]):
    def normalize_date(dt):
        if isinstance(dt, datetime):
            return dt.date()
        return dt

    # Load existing employees from company_id = 9
    existing_employees = db.session.query(Employees).filter(Employees.company_id == 9).all()
    existing_map = {emp.customer_key: emp for emp in existing_employees}

    fields_to_check = [
        "first_name", "last_name", "wa_id", "area", "role",
        "shift", "start_date", "end_date", "birth_date", "sub_area",
        "left_company"
    ]

    inserted_count = 0
    updated_count = 0
    skipped_count = 0

    for emp_data in employees_data:
        customer_key = emp_data.get('customer_key')
        if not customer_key:
            continue

        existing = existing_map.get(customer_key)

        if existing is None:
            new_emp = Employees(**emp_data)
            db.session.add(new_emp)
            inserted_count += 1
            logging.info(f"Inserted new employee with customer_key: {customer_key}")
        else:
            updated = False
            updated_fields = []
            for field in fields_to_check:
                new_value = emp_data.get(field)
                if new_value is None:
                    continue
                current_value = getattr(existing, field)

                # Normalize dates for comparison
                if field in ("start_date", "end_date", "birth_date"):
                    new_value_norm = normalize_date(new_value)
                    current_value_norm = normalize_date(current_value)
                else:
                    new_value_norm = new_value
                    current_value_norm = current_value

                if current_value_norm != new_value_norm:
                    setattr(existing, field, new_value_norm)
                    updated = True
                    updated_fields.append(field)

            if updated:
                updated_count += 1
                logging.info(f"Updated employee with customer_key: {customer_key}. Fields changed: {', '.join(updated_fields)}")
            else:
                skipped_count += 1

    db.session.commit()

    logging.info(f"Finished upsert: {inserted_count} inserted, {updated_count} updated, {skipped_count} unchanged.")

def fetch_raw_trax_data(limit=20):
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={current_app.config['SERVER_FANTASIAS']};"
        f"DATABASE=Baltra;"
        f"UID={current_app.config['UID_FANTASIAS']};"
        f"PWD={current_app.config['PWD_FANTASIAS']};"
        "TrustServerCertificate=yes;"
        "Encrypt=yes;"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Adjust WHERE clause as needed
    cursor.execute("SELECT TOP (?) * FROM Baltra_Total", limit)
    columns = [column[0].strip() for column in cursor.description]
    rows = cursor.fetchall()

    for row in rows:
        row_data = dict(zip(columns, row))
        logging.info(f"Raw Trax Data: {row_data}")

    cursor.close()
    conn.close()

def process_and_store_trax_metrics(start_date: datetime, end_date: datetime):
    records = fetch_trax_records(start_date, end_date)
    emp_map, dummy_map = build_employee_maps()
    existing_set = fetch_existing_rewards(start_date, end_date)

    # Use group_metrics to get the proper structure
    metrics = group_metrics(records)

    insert_metrics(metrics, emp_map, dummy_map, existing_set)

def fetch_trax_records(start_date, end_date):
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={current_app.config['SERVER_FANTASIAS']};"
        f"DATABASE=Baltra;"
        f"UID={current_app.config['UID_FANTASIAS']};"
        f"PWD={current_app.config['PWD_FANTASIAS']};"
        "TrustServerCertificate=yes;"
        "Encrypt=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("""
            SELECT FechaVenta, FolioTicket, internalCode, SellerID, Total, Cantidad,
                Caja, Tienda
            FROM Baltra_Total
            WHERE FechaVenta >= ? AND FechaVenta <= ?
        """, (start_date, end_date))

    columns = [col[0].strip() for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows

def build_employee_maps():
    employees = Employees.query.filter_by(company_id=9).all()
    emp_map = {e.customer_key.strip(): e.employee_id for e in employees if e.customer_key is not None}

    dummies = Employees.query.filter(
        Employees.company_id == 9,
        Employees.first_name.ilike("Dummy%"),
        Employees.active == False,
        Employees.left_company == True
    ).all()

    dummy_map = {(d.sub_area, d.area): d.employee_id for d in dummies}
    return emp_map, dummy_map

def fetch_existing_rewards(start_date, end_date):
    existing = db.session.query(
        Rewards.employee_id, Rewards.date, Rewards.metric
    ).filter(
        Rewards.company_id == 9,
        Rewards.date >= start_date,
        Rewards.date <= end_date
    ).all()
    return set((r.employee_id, r.date, r.metric) for r in existing)

def group_metrics(records):
    metrics = defaultdict(lambda: {
        "Venta Total": 0.0,
        "Tickets Totales": 0.0,
        "SKU Totales": 0.0
    })
    examples = {}

    def get_date(value):
        if isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        else:
            return None

    for record in records:
        seller_id_raw = record.get('SellerID')
        if not seller_id_raw:
            continue

        seller_id = seller_id_raw.strip()
        fecha = record.get('FechaVenta')
        date_value = get_date(fecha)
        if not date_value:
            continue  # skip invalid date

        key = (seller_id, date_value)

        metrics[key]["Venta Total"] += float(record.get("Total") or 0)
        metrics[key]["Tickets Totales"] += float(record.get("FolioTicket") or 0)
        metrics[key]["SKU Totales"] += float(record.get("internalCode") or 0)

        if key not in examples:
            examples[key] = record

    return {k: (metrics[k], examples[k]) for k in metrics}

def insert_metrics(metrics, emp_map, dummy_map, existing_set):
    inserted = 0
    updated = 0
    rewards_to_insert = []

    for (seller_id, date), (data, record) in metrics.items():
        employee_id = emp_map.get(seller_id)

        if not employee_id:
            # Try to infer dummy using sub_area and area
            sub_area = infer_sub_area(record)
            area_raw = record.get("Tienda") or ""
            area_map = {"T26": "Pedregal", "T13": "Lomas"}
            area = area_map.get(area_raw.strip(), area_raw.strip())

            # Attempt to use matching dummy
            employee_id = dummy_map.get((sub_area, area))
            if not employee_id:
                logging.warning(f"No dummy found for sub_area={sub_area}, area={area}. Falling back to 3375.")
                employee_id = 3375

        for metric, value in {
            "Venta Total": round(data["Venta Total"], 2),
            "Tickets Totales": round(data["Tickets Totales"], 2),
            "SKU Totales": round(data["SKU Totales"], 2),
        }.items():
            new_score = value

            existing_reward = db.session.query(Rewards).filter_by(
                employee_id=employee_id,
                date=date,
                metric=metric,
                company_id=9
            ).first()

            if existing_reward and existing_reward.employee_id != 3375:
                if round(float(existing_reward.score), 2) != round(float(new_score), 2):
                    existing_reward.score = new_score
                    existing_reward.week = date.isocalendar()[1]
                    existing_reward.weekday = date.weekday()
                    existing_reward.customer_key = seller_id
                    updated += 1
                    logging.info(f"Updated reward for employee {employee_id} on {date} metric '{metric}' to score {new_score}")
                # else no change, skip
            else:
                reward = Rewards(
                    employee_id=employee_id,
                    date=date,
                    week=date.isocalendar()[1],
                    metric=metric,
                    score=new_score,
                    weekday=date.weekday(),
                    company_id=9,
                    customer_key=seller_id
                )
                rewards_to_insert.append(reward)
                inserted += 1

    if rewards_to_insert:
        db.session.bulk_save_objects(rewards_to_insert)
    db.session.commit()
    logging.info(f"Inserted {inserted} new reward rows, Updated {updated} existing reward rows")

def infer_sub_area(record):
    caja = int(record.get("Caja") or 0)
    logging.info(f"Caja {caja}")
    if 10 < caja < 20:
        return "Mostrador"
    elif 40 < caja < 47:
        return "Distribuidor"
    else:
        return "Autoservicio"

def get_fetch_date_range():
    local_latest = db.session.query(db.func.max(Rewards.date)).filter(Rewards.company_id == 9).scalar()

    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={current_app.config['SERVER_FANTASIAS']};"
        f"DATABASE=Baltra;"
        f"UID={current_app.config['UID_FANTASIAS']};"
        f"PWD={current_app.config['PWD_FANTASIAS']};"
        "TrustServerCertificate=yes;"
        "Encrypt=yes;"
    )

    def query_single_date(sql):
        try:
            with pyodbc.connect(conn_str) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"Error querying database with SQL '{sql}': {e}")
            return None

    remote_latest = query_single_date("SELECT MAX(FechaVenta) FROM Baltra_Total;")
    if remote_latest is None:
        logging.error("No remote latest date found in Baltra_Total.")
        return None, None

    remote_earliest = query_single_date("SELECT MIN(FechaVenta) FROM Baltra_Total;")
    if remote_earliest is None:
        logging.error("No remote earliest date found in Baltra_Total.")
        return None, None

    if local_latest is None:
        # No local data, start at earliest remote date
        start_date = remote_earliest.date() if isinstance(remote_earliest, datetime) else remote_earliest
    else:
        # Subtract 3 days from local_latest but never before remote_earliest
        adjusted_start = local_latest - timedelta(days=3)
        earliest_date = remote_earliest.date() if isinstance(remote_earliest, datetime) else remote_earliest
        if adjusted_start < earliest_date:
            start_date = earliest_date
        else:
            start_date = adjusted_start

    end_date = remote_latest.date() if isinstance(remote_latest, datetime) else remote_latest

    if start_date > end_date:
        logging.info(f"No new data to fetch. Start date {start_date} is after end date {end_date}.")
        return None, None

    return start_date, end_date

def fetch_productos_tipo():
    logging.info("Fetching productos_tipo from Baltra_ProductosTipo")
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={current_app.config['SERVER_FANTASIAS']};"
        f"DATABASE=Baltra;"
        f"UID={current_app.config['UID_FANTASIAS']};"
        f"PWD={current_app.config['PWD_FANTASIAS']};"
        "TrustServerCertificate=yes;"
        "Encrypt=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TIPOPRODUCTO, SKU, SKUDescription, Color
        FROM Baltra_ProductosTipo
    """)

    products = defaultdict(list)
    for tipoproducto, sku, skudesc, color in cursor.fetchall():
        tipoproducto = tipoproducto.strip().lower() if tipoproducto else "otros"
        sku = str(sku).strip() if sku else "SIN_SKU"
        # Take only digits before first dash
        codigo = sku.split("-")[0] if "-" in sku else sku
        skudesc = skudesc.strip() if skudesc else "SIN_DESCRIPCION"
        color = color.strip() if color else "SIN_COLOR"

        entry = f"Art. {codigo} {skudesc} - {color}"
        products[tipoproducto].append(entry)
        logging.info(f"Added {entry} under {tipoproducto}")

    cursor.close()
    conn.close()

    # Ensure all expected keys exist
    result = {
        "promociones": products.get("promocion", []),
        "novedades": products.get("novedades", []),
        "resurtidos": products.get("resurtidos", []),
    }

    return result

def fetch_productos_top(region: str = None):
    logging.info(f"Fetching productos_top from Baltra_Productos_Top, region={region}")
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={current_app.config['SERVER_FANTASIAS']};"
        f"DATABASE=Baltra;"
        f"UID={current_app.config['UID_FANTASIAS']};"
        f"PWD={current_app.config['PWD_FANTASIAS']};"
        "TrustServerCertificate=yes;"
        "Encrypt=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    sql = "SELECT Codigo, SKUDescription FROM Baltra_Productos_Top"
    params = []
    if region:
        sql += " WHERE Region = ?"
        params.append(region)
    cursor.execute(sql, params)

    productos_top = []
    for codigo, skudesc in cursor.fetchall():
        codigo = str(codigo).strip() if codigo else "SIN_CODIGO"
        skudesc = skudesc.strip() if skudesc else "SIN_DESCRIPCION"
        entry = f"Art. {codigo} - {skudesc}"
        productos_top.append(entry)
        logging.info(f"Added top product: {entry}")

    cursor.close()
    conn.close()
    logging.info(f"Fetched {len(productos_top)} top products")

    return {"productos_top": productos_top}


def update_vector_with_product_files(productos: dict, top_products: dict):
    logging.info("Starting update_vector_with_product_files")
    client = OpenAI(api_key=current_app.config["OPENAI_KEY"])
    temp_files = []
    assistant_id = 'asst_HQGlR46PAcpe0r1wsyM9o2qJ'
    static_vector_id = 'vs_687188abe61c8191a57bcb18634a832a'

    timestamp = datetime.now().strftime("%m-%d-%H%M")

    try:
        # Create temp file for productos_tipo with a nice name
        temp_dir = tempfile.gettempdir()
        temp_prod_file_path = os.path.join(temp_dir, f"productos_tipo_{timestamp}.json")
        with open(temp_prod_file_path, "w", encoding="utf-8") as f:
            json.dump(productos, f, indent=2, ensure_ascii=False)
        logging.info(f'Productos: {json.dumps(productos)}')
        temp_files.append(temp_prod_file_path)
        logging.info(f"Created temp file for productos_tipo: {temp_prod_file_path}")

        # Create temp file for top_products with a nice name
        temp_top_file_path = os.path.join(temp_dir, f"productos_top_{timestamp}.json")
        with open(temp_top_file_path, "w", encoding="utf-8") as f:
            json.dump(top_products, f, indent=2, ensure_ascii=False)
        logging.info(f'Productos Top: {json.dumps(top_products)}')
        temp_files.append(temp_top_file_path)
        logging.info(f"Created temp file for top_products: {temp_top_file_path}")

        vector_store_files = client.vector_stores.files.list(vector_store_id=static_vector_id)
        file_ids_in_store = [file.id for file in vector_store_files.data]
        file_ids_to_keep = ["file-Y3pvR4oB7ZUUyJisk16ZGL", "file-WcLayCmgCCsVr6SyFeZyt6", "file-6vFPiU6uJDpRCZouyobZzh", "file-TXsqiFfmMZhCY1mfpg9XWS"] # Replace with your specific file IDs
        files_to_delete = [file_id for file_id in file_ids_in_store if file_id not in file_ids_to_keep]

        for file_id in files_to_delete:
            try:
                client.vector_stores.files.delete(
                    vector_store_id=static_vector_id,
                    file_id=file_id
                )
                client.files.delete(file_id=file_id)
                print(f"Successfully deleted file {file_id} from vector store {static_vector_id}.")
            except Exception as e:
                print(f"Error deleting file {file_id}: {e}")

        # Add new files to vector
        vector_files = [open(f, "rb") for f in temp_files]
        for file in vector_files:

            # Add file to the vector store
            client.vector_stores.files.upload_and_poll(
                vector_store_id=static_vector_id,
                file = file
            )

        for f in vector_files:
            f.close()

    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
                logging.info(f"Deleted temp file: {f}")

def test_fantasias(current_app):
    with current_app.app_context():
        employees = fetch_employees()
        upsert_employees(employees)

        start_date, end_date = get_fetch_date_range()
        if start_date is None or end_date is None:
            logging.info("No new data to process based on date range.")
            return

        logging.info(f"Processing data from {start_date} to {end_date}")
        process_and_store_trax_metrics(start_date, end_date)
        
        #calculate points
        if  date.today().weekday() == 0: 
            run_test(9, date.today().isocalendar()[1]-1, "weekly")
        #update charts
        generate_fantasias_charts(9)
        generate_ranking_charts(9)
        update_vector_with_product_files(fetch_productos_tipo(), fetch_productos_top())