import psycopg2
from flask import current_app
import logging
import json
import time
from datetime import datetime, timedelta
from baltra_sdk.shared.utils.date_utils import convert_date

"""
Utility file that contains a framework to run multiple queries used accross the application
"""

def get_db_params():
    """Return connection parameters for psycopg2 based on Flask config.

    Normalizes SQLAlchemy-style URLs (e.g. "postgresql+psycopg2://...") to a plain
    libpq DSN URL that psycopg2 can parse ("postgresql://...").
    """
    config = current_app.config

    database_url = (
        config.get("DATABASE_URL")
        or config.get("DB_CONNECTION_URL")
        or config.get("SQLALCHEMY_DATABASE_URI")
    )
    if database_url:
        url = str(database_url)
        # psycopg2 can't parse the SQLAlchemy dialect suffix "+psycopg2"
        if url.startswith("postgresql+psycopg2://"):
            url = "postgresql://" + url.split("postgresql+psycopg2://", 1)[1]
        elif url.startswith("postgres+psycopg2://"):
            url = "postgresql://" + url.split("postgres+psycopg2://", 1)[1]
        # Keep both postgres:// and postgresql:// as-is; both are accepted by libpq
        return {"dsn": url}

    required_keys = ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST")
    missing = [key for key in required_keys if not config.get(key)]
    if missing:
        raise RuntimeError(
            "Missing database configuration keys: " + ", ".join(missing)
        )

    return {
        "dbname": config["DB_NAME"],
        "user": config["DB_USER"],
        "password": config["DB_PASSWORD"],
        "host": config["DB_HOST"],
        "port": int(config.get("DB_PORT", 5432)),
    }

#Connect to database
def connect_to_db():
    # Database connection
    conn = psycopg2.connect(**get_db_params())
    cur = conn.cursor()
    return conn, cur

def _table_has_column(cur, table_name: str, column_name: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
          AND column_name = %s
        LIMIT 1
        """,
        (table_name, column_name),
    )
    return cur.fetchone() is not None

#Close database connection
def close_connection(conn, cur):
    # Close the connection
    cur.close()
    conn.close()

#Store webhoook object in database
def store_wa_object(status_update):
    """
    Function that stores any status update recieved in the webhook in table whatsapp_status_updates
    Update could be either a message or a status (read, delivered, sent)
    """
    logging.debug(f"Storing WA object: {status_update}")
    #conect to database
    conn, cur = connect_to_db()
    # Parse the JSON
    object_type = status_update['object']
    entry = status_update['entry'][0]
    entry_id = entry['id']
    changes = entry['changes'][0]
    messaging_product = changes['value']['messaging_product']
    metadata = changes['value']['metadata']
    phone_number_id = metadata['phone_number_id']
    field = changes['field']

    wa_id = None
    message_body = None
    timestamp = None
    conversation_id = None
    origin_type = None
    billable = None
    pricing_model = None
    category = None
    status = None
    error_info = None  # To store the entire error JSON structure
    status_id = None

    #if it is a whatsapp message the contacts field will have values
    if 'contacts' in changes['value']:
        contact = changes['value']['contacts'][0]
        wa_id = contact['wa_id']

        message = changes['value']['messages'][0]
        status_id = message['id']
        status = message['type']
        if status == "text":
            message_body = message['text']['body']
        elif status == "interactive":
            interactive_type = message['interactive']['type']
            if interactive_type == "nfm_reply":
                message_body = message['interactive']['nfm_reply']['response_json']
                status = "flow"
            elif interactive_type == "button_reply":
                message_body = message['interactive']['button_reply']["title"]
            elif interactive_type == "list_reply":
                message_body = message['interactive']['list_reply']["title"]
        elif status == "location":
            message_body = f"{message['location']['latitude']}, {message['location']['longitude']}"
        elif status == "reaction":
            emoji = message.get("reaction", {}).get("emoji", "👍")
            message_body = f"El usuario reacciono con el siguiente emoji: {emoji}"
        timestamp = message['timestamp']
    #if it is a status update the statuses field will have values
    elif 'statuses' in changes['value']:
        status_info = changes['value']['statuses'][0]
        status_id = status_info['id']
        status = status_info['status']
        timestamp = status_info['timestamp']
        wa_id = status_info['recipient_id']

        if 'conversation' in status_info:
            conversation_id = status_info['conversation']['id']
            origin_type = status_info['conversation']['origin']['type']

        if 'pricing' in status_info:
            billable = status_info['pricing']['billable']
            pricing_model = status_info['pricing']['pricing_model']
            category = status_info['pricing']['category']
        if status == "failed" and 'errors' in status_info:
            error_info = json.dumps(status_info['errors'])  # Serialize the entire error structure

    # Insert into PostgreSQL
    cur.execute('''
        INSERT INTO whatsapp_status_updates (
            object_type, entry_id, messaging_product, wa_id, phone_number_id, 
            message_body, conversation_id, origin_type, 
            billable, pricing_model, category, status, timestamp, field, status_id, error_info
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (object_type, entry_id, messaging_product, wa_id, phone_number_id, 
          message_body, conversation_id, origin_type, 
          billable, pricing_model, category, status, timestamp, field, status_id, error_info))
    # Commit the transaction
    conn.commit()
    close_connection(conn, cur)
    logging.info(f'WA object Stored in database  wa_id:{wa_id} status:{status}')

#Store sent message in database
def store_sent_message(api_response, campaign_id):
    """
    Stores an object in whatsapp_status_update with status = 'posted' every time a message is generated from the App
    This is used to track message rejections by whatsapp
    """
    try:
        conn, cur = connect_to_db()
        
        response_text = json.loads(api_response.text)
        message_id = response_text['messages'][0]['id']
        wa_id = response_text['contacts'][0].get('wa_id')
        status = "posted"
        messaging_product = response_text['messaging_product']
        timestamp = int(time.time())
        
        # Insert the data into the whatsapp_status_updates table
        cur.execute('''
            INSERT INTO whatsapp_status_updates (
                object_type, 
                messaging_product, 
                wa_id, 
                status_id,
                status,
                timestamp,
                campaign_id
            ) VALUES (
                'whatsapp_business_account', 
                %s, 
                %s, 
                %s,
                %s,
                %s,
                %s
            )
            ''', (
                messaging_product, 
                wa_id, 
                message_id,
                status,
                timestamp,
                campaign_id
            )
        )

        # Commit the transaction and close the connection
        conn.commit()
        close_connection(conn, cur)
        logging.debug(f'Sent Message Stored in database  wa_id:{wa_id} status:{status}')

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error: {error}")

#Store rejected message in database
def store_rejected_message(api_response, campaign_id, wa_id):
    """
    Stores an object in whatsapp_status_update with status = 'rejected' every time a message is rejected by whatsapp
    """
    try:
        conn, cur = connect_to_db()
        

        if isinstance(wa_id, (tuple, list)):  # check if wa_id is a tuple or list
            if len(wa_id) > 0:
                wa_id = wa_id[0]  # take the first element (expected to be the string we want)
            else:
                wa_id = ""  # handle case if tuple/list is empty, set wa_id to None or handle as needed

        response_text = json.loads(api_response.text)
        trace_id = response_text.get('fbtrace_id', '') 
        status = "rejected"
        messaging_product = response_text['error']['error_data']['messaging_product']
        timestamp = int(time.time())
        error_info = json.dumps(response_text['error'])

        
        # Insert the data into the whatsapp_status_updates table
        cur.execute('''
            INSERT INTO whatsapp_status_updates (
                object_type, 
                messaging_product, 
                wa_id, 
                status_id,
                status,
                timestamp,
                campaign_id,
                error_info
            ) VALUES (
                'whatsapp_business_account', 
                %s, 
                %s, 
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ''', (
                messaging_product, 
                wa_id, 
                trace_id,
                status,
                timestamp,
                campaign_id,
                error_info
            )
        )

        # Commit the transaction and close the connection
        conn.commit()
        close_connection(conn, cur)
        logging.info(f'Rejected Message Stored in database  wa_id:{wa_id} status:{status}')

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error: {error}")

#Function to store incoming messages in the temp_messages database for response lag 
def store_temporary_message(body):
    """
    Used only for response lag. Stores in a temporary table a message for a brief period (= lag) so if other
    messages are recieved only 1 response is triggered
    """
    conn, cur = connect_to_db()
    value = body['entry'][0]['changes'][0]['value']
    wa_id = value['contacts'][0]['wa_id']
    message = value['messages'][0]
    message_id = message['id']

    # Derive WhatsApp type and interactive subtype
    raw_type = message.get('type')
    interactive_type = None
    if raw_type == 'interactive':
        interactive_type = (message.get('interactive') or {}).get('type')
    # Normalize to our priority rules (only button/list are interactive-priority)
    if raw_type == 'interactive' and interactive_type not in {'button_reply', 'list_reply'}:
        normalized_type = 'flow' if interactive_type == 'nfm_reply' else raw_type
    else:
        normalized_type = raw_type

    # Map to IDs if catalog is present
    wa_type_id = 1 if normalized_type == 'text' else (2 if normalized_type == 'interactive' else None)
    wa_interactive_type_id = None
    if normalized_type == 'interactive':
        if interactive_type == 'button_reply':
            wa_interactive_type_id = 1
        elif interactive_type == 'list_reply':
            wa_interactive_type_id = 2

    # Build dynamic insert depending on available columns
    has_wa_type = _table_has_column(cur, 'temp_messages', 'wa_type')
    has_wa_interactive_type = _table_has_column(cur, 'temp_messages', 'wa_interactive_type')
    has_wa_type_id = _table_has_column(cur, 'temp_messages', 'wa_type_id')
    has_wa_interactive_type_id = _table_has_column(cur, 'temp_messages', 'wa_interactive_type_id')

    columns = ["message_id", "wa_id", "body"]
    values = [message_id, wa_id, json.dumps(body)]
    if has_wa_type:
        columns.append("wa_type")
        values.append(normalized_type)
    if has_wa_interactive_type:
        columns.append("wa_interactive_type")
        values.append(interactive_type)
    if has_wa_type_id:
        columns.append("wa_type_id")
        values.append(wa_type_id)
    if has_wa_interactive_type_id:
        columns.append("wa_interactive_type_id")
        values.append(wa_interactive_type_id)

    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO temp_messages ({', '.join(columns)}) VALUES ({placeholders})"
    cur.execute(sql, tuple(values))
    conn.commit()
    close_connection(conn, cur)
    logging.debug(f'Message Stored in Temp Database  wa_id:{wa_id} id:{message_id}')

#Fetch all messages for a certain wa_id in the temp_messages table
def fetch_temporary_messages(body, lag):
    """
    Used only for response lag. Fetches temporary messages that are later on concatenated
    """
    conn, cur = connect_to_db()
    wa_id = body['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
    # Prefer received_at if present; fall back to legacy timestamp
    if _table_has_column(cur, 'temp_messages', 'received_at'):
        time_col = 'received_at'
    else:
        time_col = 'timestamp'
    cur.execute(f"SELECT * FROM temp_messages WHERE wa_id = %s AND {time_col} >= NOW() - INTERVAL %s", (wa_id, f"{lag} seconds"))
    messages = cur.fetchall()
    close_connection(conn, cur)
    return messages

#mark killed instances in whatsapp_status_updates
def update_lag_killed(body):
    """
    Every time the app decides not to generate a response for a user message due to lag, it marks it as "killed" 
    """
    status_id = body['entry'][0]['changes'][0]['value']['messages'][0]['id']
    conn, cur = connect_to_db()

    # Execute the update query
    cur.execute(
        """
        UPDATE whatsapp_status_updates
        SET lag_killed = TRUE
        WHERE status_id = %s
        """,
        (status_id,)
    )
    
    # Commit the changes
    conn.commit()
    
    # Check if the update was successful
    if cur.rowcount != 0:
        logging.info(f'Message {status_id} killed due to lag')
    close_connection(conn, cur)
    
#delete all messages from a certain wa_id in the temp_messages table
def delete_temp_database(body):
    """
    Only used for response lag, deletes temporary database once a response is triggered
    """
    conn, cur = connect_to_db()
    wa_id = body['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
    cur.execute(
        """
        DELETE FROM temp_messages
        WHERE wa_id = %s
        """,
        (wa_id,)
    )
    conn.commit()
    if cur.rowcount != 0:
        logging.info(f"Successfully deleted {cur.rowcount} record(s) for wa_id: {wa_id}")

def mark_messages_as_processing(body):
    """
    Marks all temp_messages from a given wa_id as processing = TRUE.
    Used when a response is triggered to prevent reprocessing.
    """
    conn, cur = connect_to_db()
    wa_id = body['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
    cur.execute(
        """
        UPDATE temp_messages
        SET processing = TRUE
        WHERE wa_id = %s
        """,
        (wa_id,)
    )
    conn.commit()
    if cur.rowcount != 0:
        logging.info(f"Marked {cur.rowcount} record(s) as processing for wa_id: {wa_id}")

def are_messages_being_processed(body):
    """
    Checks if there are any temp_messages for the given wa_id currently marked as processing.
    Returns True if any exist, otherwise False.
    """
    conn, cur = connect_to_db()
    wa_id = body['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM temp_messages
            WHERE wa_id = %s AND processing = TRUE
        )
        """,
        (wa_id,)
    )
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

#Get scheduled messages from scheduled_messages table
def get_scheduled_messages():
    """
    Used in the schedulers to fetch push notifications due
    """
    # Step 1: Connect to the database
    conn, cur = connect_to_db()

    # Step 2: Query the scheduled_messages table
    query = """
        SELECT id, template, company_id, sender, parameters,  send_time, recurring_interval
        FROM scheduled_messages
        WHERE send_time <= NOW() AND status = 'pending';
    """
    
    cur.execute(query)
    scheduled_messages = cur.fetchall()
    close_connection(conn, cur)
    return scheduled_messages

#Get whatsapp ids that match certain parameters
def get_whatsapp_ids(company_id, params):
    """
    Fetches wa_ids matching filters. Supports:
    - direct equality (e.g., "role": "X")
    - multiple values with IN (e.g., "role": ["X", "Y"])
    - exclusion with NOT or NOT IN (e.g., "exclude_area": "X" or ["X", "Y"])
    """
    conn, cur = connect_to_db()
    employee_query = """
        SELECT wa_id 
        FROM employees 
        WHERE company_id = %s 
    """
    query_params = [company_id]

    for key, value in params.items():
        if key == 'entry_date_condition':
            employee_query += " AND start_date <= NOW() - INTERVAL %s"
            query_params.append(value)
        elif key == 'new_date_condition':
            employee_query += " AND start_date >= NOW() - INTERVAL %s"
            query_params.append(value)
        elif key == 'onboarding_days':
            employee_query += " AND DATE(start_date + make_interval(days := %s)) = DATE(NOW())"
            query_params.append(value)
        elif key == 'birth_date' and value:
            employee_query += " AND TO_CHAR(birth_date, 'MM-DD') = TO_CHAR(NOW(), 'MM-DD')"
        elif key == 'start_date' and value:
            employee_query += " AND TO_CHAR(start_date, 'MM-DD') = TO_CHAR(NOW(), 'MM-DD')"
        elif key.startswith("exclude_"):
            column = key.replace("exclude_", "")
            if isinstance(value, list):
                placeholders = ','.join(['%s'] * len(value))
                employee_query += f" AND {column} NOT IN ({placeholders})"
                query_params.extend(value)
            else:
                employee_query += f" AND {column} != %s"
                query_params.append(value)
        else:
            if isinstance(value, list):
                placeholders = ','.join(['%s'] * len(value))
                employee_query += f" AND {key} IN ({placeholders})"
                query_params.extend(value)
            else:
                employee_query += f" AND {key} = %s"
                query_params.append(value)

    cur.execute(employee_query, query_params)
    wa_ids = cur.fetchall()
    close_connection(conn, cur)
    return wa_ids

#Reschedule messages in scheduled_messages table after they're sent
def reschedule_message(new_send_time, id):
    """
    Reschedule messages in scheduled_messages table after they're sent based on theri recurring interval
    """
    conn, cur = connect_to_db()

    cur.execute(
        """
        UPDATE scheduled_messages
        SET send_time = %s
        WHERE id = %s
        """,
        (new_send_time, id)
    )
    conn.commit()
    logging.info(f'Rescheduled Message {id} for {new_send_time}')
    close_connection(conn, cur)

#Cancel scheduled messages with unkown intervals
def cancel_message(id):
    """
    If scheduled messages don't have a valid recurring interval, this function cancels them  
    """
    conn, cur = connect_to_db()

    cur.execute(
        """
        UPDATE scheduled_messages
        SET status = 'canceled'
        WHERE id = %s
        """,
        (id, )
    )
    conn.commit()
    logging.info(f'Canceled Message {id}')
    close_connection(conn, cur)

#Campaign data fetching
def fetch_campaign_data():
    """
    Fetches the relevant information to send to Baltra operations team a daily summary of messages sent in past 24hours
    """
    query = """
    WITH campaign_status_ids AS (
        SELECT DISTINCT
            status_id,
            campaign_id
        FROM
            whatsapp_status_updates
        WHERE
            campaign_id IS NOT NULL
            AND timestamp >= EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - INTERVAL '24 HOURS'))
    ),
    status_counts AS (
        SELECT
            c.campaign_id,
            w.status,
            COUNT(*) AS count
        FROM
            whatsapp_status_updates w
        JOIN
            campaign_status_ids c
            ON w.status_id = c.status_id
        GROUP BY
            c.campaign_id, w.status
    )
    SELECT
        campaign_id,
        COALESCE(SUM(CASE WHEN status = 'posted' THEN count ELSE 0 END), 0) AS messages_posted,
        COALESCE(SUM(CASE WHEN status = 'rejected' THEN count ELSE 0 END), 0) AS messages_rejected,
        COALESCE(SUM(CASE WHEN status = 'failed' THEN count ELSE 0 END), 0) AS messages_failed,
        COALESCE(SUM(CASE WHEN status = 'sent' THEN count ELSE 0 END), 0) AS messages_sent,
        COALESCE(SUM(CASE WHEN status = 'delivered' THEN count ELSE 0 END), 0) AS messages_delivered,
        COALESCE(SUM(CASE WHEN status = 'read' THEN count ELSE 0 END), 0) AS messages_read
    FROM
        status_counts
    GROUP BY
        campaign_id;
    """
    
    conn, cur = connect_to_db()    
    
    with conn.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
    
    close_connection(conn, cur)
    message = "id         |posted|rejected|failed|sent|delivered|read\n"
    for row in data:
        campaign_id, messages_posted,messages_rejected ,messages_failed, messages_sent, messages_delivered, messages_read = row
        message += f"{campaign_id}|{messages_posted}    |{messages_rejected}    |{messages_failed}    |{messages_sent}   |{messages_delivered}     |{messages_read}"
        message += "\n"

    return message

#Messages due fetching
def fetch_due_messages():
    """
    Fetches the relevant information to send to Baltra operations team a daily summary of messages due in next 24 hours
    """

    query = """
    SELECT
        company_id,
        template,
        send_time
    FROM
        scheduled_messages
    WHERE
        status = 'pending'
        AND send_time BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '24 HOURS'
    ORDER BY company_id, send_time;
    """
    
    conn, cur = connect_to_db()
    
    with conn.cursor() as cursor:
        cursor.execute(query)
        due_messages = cursor.fetchall()
    
    close_connection(conn, cur)
    # Initialize an empty string to store all the messages
    message = "company_id|Send_time|Template\n"
    
    for msg in due_messages:
        company_id, template, send_time= msg
        send_time = send_time.strftime("%H:%M")
        # Format the message for each due message
        message += f"{company_id}         |{send_time}    |{template}"
        message += "\n" 
    
    # Remove the last separator and return the final concatenated string
    return message

#Get unique employee_ids based on company_id and days since they sent their last message
def get_unique_employee_ids(company_id, days=7):
    """
    Get unique employee_ids based on company_id and days since they sent their last message. This is used in get_sentiment and get_candidates
    xcludes employees with role 'Business Owner', as it is used to extract sentiment and to extract candidates.
    """
    conn, cur = connect_to_db()
    cur.execute("""
        SELECT DISTINCT m.employee_id
        FROM messages m
        JOIN employees e ON m.employee_id = e.employee_id
        WHERE m.company_id = %s
        AND m.time_stamp > NOW() - INTERVAL '%s DAY'
        AND e.role != 'Business Owner'
        ORDER BY m.employee_id;
    """, 
    (company_id, days)
    )
    result = [row[0] for row in cur.fetchall()]
    close_connection(conn, cur)
    return result

# Fetch messages for a batch of employees based on a day interval
def get_messages_for_batch(employee_ids, company_id, days=7):
    """
    Get messages based on employee_id and days since they sent their last message. This is used in get_sentiment and get_candidates
    """
    conn, cur = connect_to_db()

    cur.execute("""
        SELECT employee_id, sent_by, message_body
        FROM messages 
        WHERE company_id = %s 
        AND time_stamp > NOW() - INTERVAL '%s DAYS'
        AND employee_id IN %s
        ORDER BY employee_id, time_stamp;
    """, (company_id, days, employee_ids))
    result = cur.fetchall()
    close_connection(conn, cur)
    return result

# Fetch attendance data used for failed function implemented in saks 
def fetch_attendance_data(company_id):
    """
    Fetches attendance confirmations to be sent to business owner. Used for saks but experiment failed
    """
    conn, cur = connect_to_db()    
    query_absence = """
    SELECT DISTINCT ON (m.wa_id)
        e.first_name,
        e.last_name, e.role, e.shift, e.wa_id
    FROM messages m
    JOIN employees e ON e.wa_id = m.wa_id
    WHERE m.message_body = 'no-asistiré-button'
    AND m.time_stamp >= NOW() - INTERVAL '6 HOUR'
    AND e.company_id = %s;
    """
    
    with conn.cursor() as cursor:
        cursor.execute(query_absence, (company_id,))
        data_absense = cursor.fetchall()

    message = "*Faltas Confirmadas:*\n"
    for row in data_absense:
        first_name, last_name, role, shift, wa_id = map(lambda x: x if x is not None else '', row)
        message += f"❌ {(first_name + ' ' + last_name)[:40]}, {role}"
        message += "\n"

    query_confirmed = """
    SELECT DISTINCT ON (m.wa_id)
        e.first_name,
        e.last_name, e.role, e.shift, e.wa_id
    FROM messages m
    JOIN employees e ON e.wa_id = m.wa_id
    WHERE m.message_body = 'si-asistiré-button'
    AND m.time_stamp >= NOW() - INTERVAL '6 HOUR'
    AND e.company_id = %s;
    """

    with conn.cursor() as cursor:
        cursor.execute(query_confirmed, (company_id,))
        data_confirmed = cursor.fetchall()

    message += "*Asistencias Confirmadas:*\n"
    for row in data_confirmed:
        first_name, last_name, role, shift, wa_id = map(lambda x: x if x is not None else '', row)
        message += f"✅ {(first_name + ' ' + last_name)[:40]}, {role}"
        message += "\n"

    # Extract wa_ids for the no-response query
    wa_id_response = [row[4] for row in data_absense + data_confirmed]

    campaign_id = f"{company_id}-confirmar_asistencia_push"
    query_no_response = """
    SELECT DISTINCT 
    e.first_name, 
    e.last_name, 
    e.role, 
    e.shift 
    FROM 
    whatsapp_status_updates wsu
    JOIN 
    employees e ON wsu.wa_id = e.wa_id
    WHERE 
    wsu.campaign_id = %s
    AND e.wa_id NOT IN %s
    AND TO_TIMESTAMP(wsu.timestamp) >= NOW() - INTERVAL '6 HOUR';
    """

    #Ensure that if wa_id_response is empty it won't crash the query as it needs a value
    wa_id_response = wa_id_response or ["5555555555555"]

    with conn.cursor() as cursor:
        cursor.execute(query_no_response, (campaign_id, tuple(wa_id_response)))
        data_no_response = cursor.fetchall()

    message += "*Sin respuesta:*\n"
    for row in data_no_response:
        first_name, last_name, role, shift = map(lambda x: x if x is not None else '', row)
        message += f"◽ {(first_name + ' ' + last_name)[:40]}, {role}"
        message += "\n"

    close_connection(conn, cur)
    return message

#get employee unique wa_ids based on dates
def get_unique_employee_ids_points(start_date):
    """
    Fetches unique employee ids based on a date, used in red flags
    """
    conn, cur = connect_to_db()
    cur.execute("""
        SELECT DISTINCT employee_id 
        FROM messages 
        WHERE time_stamp >= %s 
        ORDER BY employee_id;
    """, 
    (start_date,)
    )
    result = [row[0] for row in cur.fetchall()]
    close_connection(conn, cur)
    return result

# Fetch messages for a batch of employees using a date
def get_messages_for_batch_rewards(employee_ids, start_date):
    """
    Fetches conversations based on employee ids and a date, used in red flags
    """
    conn, cur = connect_to_db()

    cur.execute("""
        SELECT employee_id, company_id, sent_by, message_body
        FROM messages  
        WHERE time_stamp >= %s
        AND employee_id IN %s
        ORDER BY employee_id, time_stamp;
    """, (start_date, employee_ids))
    result = cur.fetchall()
    close_connection(conn, cur)
    return result

#Stores red flags
def store_flag(flag_item):
    """
    Stores a flagged conversation in the flagged_conversations table.

    Input should be a dict with the following format:
    {
        'assistant_id': 'rewards_assistant', 
        'employee_id': '2243', 
        'company_id': '5', 
        'action': 'canje', 
        'requested_reward': 'tarjeta $200 Walmart', 
        'justification': 'El colaborador solicitó explícitamente canjear sus puntos por la tarjeta de Walmart.'
    }
    Some values can be empty, and the function should handle them safely.
    """
    try:
        conn, cur = connect_to_db()
        logging.debug(f'Sotoring item: {flag_item}')
        # Define default values for missing or empty keys
        assistant_id = flag_item.get("assistant_id", None) or None
        employee_id = flag_item.get("employee_id", None)
        company_id = flag_item.get("company_id", None)
        action = flag_item.get("action", None) or None
        requested_reward = flag_item.get("requested_reward", None) or None
        justification = flag_item.get("justification", None) or None

        # Convert to integer only if values exist, otherwise store as NULL
        employee_id = int(employee_id) if employee_id else None
        company_id = int(company_id) if company_id else None

        # Insert query for flagged_conversations table
        query = """
            INSERT INTO flagged_conversations 
            (assistant_id, employee_id, company_id, action, requested_reward, justification)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        
        values = (assistant_id, employee_id, company_id, action, requested_reward, justification)

        cur.execute(query, values)
        conn.commit()

        logging.debug("Flagged conversation stored successfully.")

    except Exception as e:
        logging.error(f"Error inserting flagged conversation: {e}")

    finally:
        close_connection(conn, cur)

#Function to store a message in the postgre db
def add_msg_to_db(message_id, employee_data, sent_by, message_body, whatsapp_msg_id):
    """
    Store in messages database, used in openai_assistant
    """
    try:
        conn, cur = connect_to_db()

        wa_id = employee_data.get("wa_id")  # get the value of wa_id, might be string or tuple/list

        if isinstance(wa_id, (tuple, list)):  # check if wa_id is a tuple or list
            if len(wa_id) > 0:
                wa_id = wa_id[0]  # take the first element (expected to be the string we want)
            else:
                wa_id = ""  # handle case if tuple/list is empty, set wa_id to None or handle as needed


        # Insert the new message into the messages table
        insert_message_query = """
        INSERT INTO messages (wa_id, employee_id, company_id, message_id, thread_id, time_stamp, sent_by, message_body, conversation_type, whatsapp_msg_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(insert_message_query, (
            wa_id,
            employee_data["employee_id"],
            employee_data["company_id"],
            message_id,
            employee_data["thread_id"],
            datetime.now(),
            sent_by,
            message_body,
            employee_data["conversation_type"],
            whatsapp_msg_id
        ))
        conn.commit()
        logging.info(f"{sent_by} Message for wa_id: {employee_data['wa_id']} stored successfully.")

    except Exception as e:
        logging.error(f"Error: {e}")
    
    finally:
        close_connection(conn, cur)

#Function to record a prize redemption
def record_prize_redemption(employee_data, points_redeemed, date_str):
    """
    Records a prize redemption by inserting a record into the Points and Redemptions table.
    
    Args:
        employee_data (dict): Dictionary containing employee information
        points_redeemed (int): Number of points redeemed for the prize
        
    Returns:
        bool: True if the record was successfully inserted, False otherwise
    """
    try:
        # Connect to the PostgreSQL database
        conn, cur = connect_to_db()        
        current_date = datetime.now()
        current_week = current_date.isocalendar()[1]

        # Fetch prize_id from the prizes table based on company_id and points_redeemed
        cur.execute("""
            SELECT prize_id FROM prizes
            WHERE company_id = %s AND puntos = %s AND active = true
            LIMIT 1;
        """, (employee_data["company_id"], points_redeemed))
                
        prize_row = cur.fetchone()
        if not prize_row:
            logging.error(f"No prize found for company_id {employee_data['company_id']} with {points_redeemed} points.")
            return False
        prize_id = prize_row[0]

        # Get the estimated delivery date using the helper function
        estimated_delivery_date = convert_date(date_str)

        # Insert negative points transaction to reflect redemption
        insert_points_query = """
        INSERT INTO points (company_id, week, transaction, points, employee_id, date, area, metric)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING points_id;
        """
        cur.execute(insert_points_query, (
            employee_data["company_id"],
            current_week,
            "points redeemed",
            -abs(points_redeemed),  # Ensure points are negative
            employee_data["employee_id"],
            current_date,
            employee_data["area"],
            "prize claim"
        ))

        # Get the points_id generated by the points insert
        points_id = cur.fetchone()[0]

        # Insert the redemption record into the redemptions table
        insert_redemption_query = """
        INSERT INTO redemptions (points_id, prize_id, estimated_delivery_date, date_requested)
        VALUES (%s, %s, %s, %s);
        """
        cur.execute(insert_redemption_query, (
            points_id,
            prize_id,
            estimated_delivery_date,
            current_date
        ))

        conn.commit()
        logging.info(f"Prize redemption recorded for employee {employee_data['employee_id']} with {points_redeemed} points")
        return True
        
    except Exception as e:
        logging.error(f"Error recording prize redemption: {e}")
        return False
    
    finally:
        close_connection(conn, cur)

#Get whatsapp ids from company_id
def get_wa_ids(company_id):
    """
    Returns a list of wa_ids where active = true where company_id = company_id
    Used in push_messages 
    """
    conn, cur = connect_to_db()

    try:
        # Define the query string
        query = """
            SELECT wa_id
            FROM employees
            WHERE company_id = %s
            AND active = true;
        """
        # Execute the query with parameters
        cur.execute(query, (company_id,))
        
        # Fetch the results
        wa_ids = cur.fetchall()
        return [wa_id[0] for wa_id in wa_ids]
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []
    
    finally:
        close_connection(conn, cur)

#Get whatsapp ids from company_id and role is business owner
def get_wa_ids_owner(company_id):
    """
    Returns a list of wa_ids where active = true and role = 'Business Owner' where company_id = company_id
    Used in push_messages
    """
    conn, cur = connect_to_db()

    try:
        # Define the query string
        query = """
            SELECT wa_id
            FROM employees
            WHERE company_id = %s
            AND role = 'Business Owner';
        """
        # Execute the query with parameters
        cur.execute(query, (company_id,))
        
        # Fetch the results
        wa_ids = cur.fetchall()
        return [wa_id[0] for wa_id in wa_ids]
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []
    
    finally:
        close_connection(conn, cur)

def log_response_time(employee_id, company_id, start_time, end_time, time_delta):
    """
    log time it takes for an asisstant to generate a response
    """
    conn, cur = connect_to_db()

    try:
        cur.execute("""
            INSERT INTO response_timings (employee_id, company_id, start_time, end_time, time_delta)
            VALUES (%s, %s, %s, %s, %s)
        """, (employee_id, company_id, start_time, end_time, time_delta))
        conn.commit()
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    finally:
        close_connection(conn, cur)

def store_sentiment_data(processed_data):
    """
    Stores sentiment analysis results in the sentiment table.

    Args:
        processed_data: List of dictionaries containing sentiment data with the following keys:
            - employee_id
            - company_id
            - date
            - week
            - metric
            - score
            - question

    Returns:
        bool: True if data was stored successfully, False otherwise
    """
    try:
        conn, cur = connect_to_db()

        # Updated insert query to include `question`
        insert_query = """
        INSERT INTO sentiment (
            employee_id, company_id, date, week, metric, score, question
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
        );
        """

        for record in processed_data:
            cur.execute(insert_query, (
                record['employee_id'],
                record['company_id'],
                record['date'],
                record['week'],
                record['metric'],
                record['score'],
                record['question']  # ✅ new field
            ))

        conn.commit()
        logging.info(f"Successfully stored {len(processed_data)} sentiment records")
        return True

    except Exception as e:
        logging.error(f"Error storing sentiment data: {e}")
        return False

    finally:
        close_connection(conn, cur)


def fetch_conversations_insights(company_id):
    query = """
        SELECT
            m.employee_id,
            m.sent_by,
            m.message_body,
            e.sub_area
        FROM
            messages m
        JOIN
            employees e ON m.employee_id = e.employee_id
        WHERE
            m.company_id = %s
            AND m.sent_by = 'user'
            AND m.time_stamp > NOW() - INTERVAL '7 DAY'
        ORDER BY
            m.employee_id, m.time_stamp;
    """

    conn, cur = connect_to_db()
    cur.execute(query, (company_id,))
    result = cur.fetchall()
    close_connection(conn, cur)

    return result

def get_company_9_weekly_stats(employee_id: int) -> dict:
    try:
        conn, cur = connect_to_db()

        # 1. Weekly stats query
        weekly_query = """
            SELECT
                week,
                metric,
                SUM(score::float) AS total_score
            FROM
                rewards
            WHERE
                employee_id = %s
                AND company_id = 9
                AND metric IN ('Venta Total', 'Tickets Totales', 'SKU Totales')
            GROUP BY
                week, metric
            ORDER BY
                week DESC
            LIMIT 6
        """
        cur.execute(weekly_query, (employee_id,))
        weekly_rows = cur.fetchall()

        semanas = sorted(set(row[0] for row in weekly_rows), reverse=True)[:2]
        if len(semanas) < 2:
            semanas += [0] * (2 - len(semanas))

        semana_actual, semana_pasada = semanas[0], semanas[1]

        weekly_data = {
            semana_actual: {'Venta Total': 0, 'Tickets Totales': 0, 'SKU Totales': 0},
            semana_pasada: {'Venta Total': 0, 'Tickets Totales': 0, 'SKU Totales': 0},
        }

        for row in weekly_rows:
            week, metric, total_score = row
            if week in weekly_data:
                weekly_data[week][metric] = total_score

        # 2. Daily stats for yesterday
        yesterday = (datetime.now() - timedelta(hours=6)).date() - timedelta(days=1)

        daily_query = """
            SELECT
                metric,
                SUM(score::float) AS total_score
            FROM
                rewards
            WHERE
                employee_id = %s
                AND company_id = 9
                AND date = %s
                AND metric IN ('Venta Total', 'Tickets Totales', 'SKU Totales')
            GROUP BY
                metric
        """
        cur.execute(daily_query, (employee_id, yesterday))
        daily_rows = cur.fetchall()

        daily_data = {'Venta Total': 0, 'Tickets Totales': 0, 'SKU Totales': 0}
        for metric, total_score in daily_rows:
            daily_data[metric] = total_score

        close_connection(conn, cur)

        def safe_div(a, b):
            return round(a / b, 2) if b else 0


        return {
            # Weekly
            "venta_total_semana_actual": weekly_data[semana_actual]['Venta Total'],
            "venta_total_semana_pasada": weekly_data[semana_pasada]['Venta Total'],
            "total_tickets_semana_actual": weekly_data[semana_actual]['Tickets Totales'],
            "total_tickets_semana_pasada": weekly_data[semana_pasada]['Tickets Totales'],
            "ticket_promedio_semana_actual": safe_div(weekly_data[semana_actual]['Venta Total'], weekly_data[semana_actual]['Tickets Totales']),
            "ticket_promedio_semana_pasada": safe_div(weekly_data[semana_pasada]['Venta Total'], weekly_data[semana_pasada]['Tickets Totales']),
            "skus_por_ticket_semana_actual": safe_div(weekly_data[semana_actual]['SKU Totales'], weekly_data[semana_actual]['Tickets Totales']),
            "skus_por_ticket_semana_pasada": safe_div(weekly_data[semana_pasada]['SKU Totales'], weekly_data[semana_pasada]['Tickets Totales']),
            "venta_total_dia_anterior": daily_data['Venta Total'],
            "total_tickets_dia_anterior": daily_data['Tickets Totales'],
            "ticket_promedio_dia_anterior": safe_div(daily_data['Venta Total'], daily_data['Tickets Totales']),
            "sku_por_ticket_dia_anterior": safe_div(daily_data['SKU Totales'], daily_data['Tickets Totales']),
        }

    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {
            "venta_total_semana_actual": 0,
            "venta_total_semana_pasada": 0,
            "total_tickets_semana_actual": 0,
            "total_tickets_semana_pasada": 0,
            "ticket_promedio_semana_actual": 0,
            "ticket_promedio_semana_pasada": 0,
            "skus_por_ticket_semana_actual": 0,
            "skus_por_ticket_semana_pasada": 0,

            "venta_total_dia_anterior": 0,
            "total_tickets_dia_anterior": 0,
            "ticket_promedio_dia_anterior": 0,
            "sku_promedio_dia_anterior": 0,
        }

def process_employee_metrics(performance_data):
    grouped = {}

    for entry in performance_data:
        date = entry["date"]
        metric = entry["metric"]
        score = entry["score"]

        if date not in grouped:
            grouped[date] = {}

        grouped[date][metric] = score
    # Sort the dictionary by date keys (assuming date format 'YYYY-MM-DD')
    sorted_grouped = dict(sorted(grouped.items(), key=lambda x: x[0]))

    return sorted_grouped

def clean_prizes(prizes):
    cleaned = []
    i = 1
    while f"premio_{i}" in prizes:
        if prizes.get(f"boolean_{i}"):
            cleaned.append({
                "name": prizes.get(f"premio_{i}"),
                "points": prizes.get(f"puntos_{i}"),
                "description": prizes.get(f"desc_{i}")
            })
        i += 1
    return cleaned
