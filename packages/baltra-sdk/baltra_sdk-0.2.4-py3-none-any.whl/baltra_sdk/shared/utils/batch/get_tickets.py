import pandas as pd
import numpy as np
import json
import logging
from baltra_sdk.shared.utils.postgreSQL_utils import fetch_conversations_insights
from baltra_sdk.shared.utils.openai_assistant import get_openai_client
from flask import current_app
import click
from datetime import datetime
import time  # Import time module
from openai import OpenAI, AssistantEventHandler, APITimeoutError
from typing_extensions import override



# Classify conversation data
def get_insights(conversation_data, client, assistant_id):
    """
    Sends conversation data to the OpenAI assistant to get insights.

    Args:
        conversation_data: List of tuples (employee_id, sent_by, message_body, sub_area).
        client: The OpenAI client instance.
        assistant_id: The ID of the OpenAI assistant.

    Returns:
        A JSON object with the assistant's classification results.
    """
    try:
        input_data = "\n".join([
            f"{emp_id}, {sent_by}, {msg}, {sub_area}"
            for emp_id, sent_by, msg, sub_area in conversation_data
        ])

        # Create a new thread with OpenAI
        thread = client.beta.threads.create()

        # Add the formatted data to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=input_data
        )

        openai_start_time = time.time()

        handler = EventHandler()
        with client.beta.threads.runs.stream(
            assistant_id=assistant_id,
            thread_id=thread.id,
            event_handler=handler,
        ) as stream:
            stream.until_done()


        # Time it took for OpenAI to respond
        openai_end_time = time.time()
        openai_response_time = openai_end_time - openai_start_time

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = handler.full_text  # buffered full response from EventHandler

        # Check if the response is a valid JSON
        try:
            return json.loads(response), openai_response_time
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
            return None, None
    except Exception as e:
        logging.error(f"Error in get_insights: {e}")
        return None, None

#Helper for streaming assistant responses
class EventHandler(AssistantEventHandler):
    """
    Minimal event handler for streaming assistant responses.
    It collects text fragments (deltas) into a single string buffer,
    so you get the full message after streaming completes.
    """

    def __init__(self):
        super().__init__()
        self.full_text = ""  # Buffer to accumulate all text chunks

    @override
    def on_text_delta(self, delta, snapshot):
        # Called each time a new chunk of text is received.
        # Append the new chunk to the full_text buffer.
        self.full_text += delta.value

    # Other event hooks can be added if you want to handle special cases like tool calls.


# Process batches of employees
def process_company(company_id, date_str):
    """
    Fetches raw conversations and gets insights using OpenAI assistant for a given company and date.

    Args:
        company_id: The company ID.
        date_str: The reference date in "MM/DD/YYYY" format.

    Returns:
        A pandas DataFrame with insights data.
    """
    assistant_id = 'asst_8zymqBg6jehfFJAlUXuVuD8V'
    client = get_openai_client()
    raw_conversations = fetch_conversations_insights(company_id)

    # Get insights from OpenAI
    batch_results, response_time = get_insights(raw_conversations, client, assistant_id)
    grouped_data = batch_results.get('tickets', [])  # Use .get() to avoid KeyError

    # Ensure all items have the required fields, especially 'theme'
    for item in grouped_data:
        if 'theme' not in item:
            logging.warning(f"Falta 'theme' en: {item}")
            item['theme'] = None  # Add missing theme field with None value
        
        # Ensure other fields exist as well
        required_fields = ['category', 'title', 'body', 'area', 'frequency', 'assigned_to']
        for field in required_fields:
            if field not in item:
                item[field] = None

    df = pd.json_normalize(grouped_data)
    if df.empty:
        logging.warning(f"No valid data to process for company_id {company_id}")
    else:
        df['company_id'] = company_id
        df['date'] = date_str
        df['active'] = 1     
        #status is open for tickets and null for comments (negative and positive)   
        df['status'] = np.where(df['category'] == 'ticket', 'Abierto', None)

        #Rearenge the df in the same order as the db
        desired_order = [
            'company_id', 'date', 'week', 'category', 'body', 'active',
            'area', 'title', 'status', 'frequency', 'assigned_to', 'theme']
        df = df.reindex(columns=desired_order)


        try:
            # Handle date parsing and get the week number
            df['week'] = datetime.strptime(date_str, "%m/%d/%Y").isocalendar().week
        except ValueError as e:
            logging.error(f"Date format error for {date_str}: {e}")
            return pd.DataFrame(), response_time  # Return an empty DataFrame if date format is wrong

    return df, response_time

# Convert insights to CSV
def json_to_csv(df, date_str):
    """
    Converts classification results to a CSV file.

    Args:
        df: DataFrame with insight results.
        date_str: The reference date string.

    Returns:
        None
    """
    try:
        if not df.empty:
            csv_file = f'tickets_{date_str}.csv'
            df.to_csv(csv_file, index=False)
            logging.info(f"Data successfully saved to {csv_file}")
        else:
            logging.warning("Empty DataFrame received for CSV conversion.")
    except Exception as e:
        logging.error(f"Error in json_to_csv: {e}")

# Main function
def get_tickets(date_str):
    """
    Orchestrates the full process of fetching conversations, classifying them, and saving results.

    Args:
        date_str: The reference date in "MM/DD/YYYY" format.

    Returns:
        None
    """
    starting_time = time.time()
    company_ids = [4, 5, 7, 8, 9, 10]
    # Modify this line to replace slashes with dashes or underscores
    csv_file = f'tickets_{date_str.replace("/", "-")}.csv'

    week = None

    try:
        for i, company_id in enumerate(company_ids):
            company_start_time = time.time()

            logging.info(f'Processing company_id: {company_id}')
            insights_df, openai_response_time  = process_company(company_id, date_str)

            if not insights_df.empty:
                if week is None:
                    week = insights_df['week'].iloc[0]

                total_count = len(insights_df)
                positive_count = len(insights_df[insights_df['category'] == 'positive'])
                negative_count = len(insights_df[insights_df['category'] == 'negative'])
                ticket_count = len(insights_df[insights_df['category'] == 'ticket'])

                # Log counts for each category
                logging.info(f"Company ID: {company_id}")
                logging.info(f"Total insights: {total_count}")
                logging.info(f"Positive insights: {positive_count}")
                logging.info(f"Negative insights: {negative_count}")
                logging.info(f"Ticket insights: {ticket_count}")

                # Append to CSV
                write_mode = 'w' if i == 0 else 'a'
                header = i == 0  # Write header only once
                try:
                    insights_df.to_csv(csv_file, mode=write_mode, header=header, index=False, encoding = 'latin1')
                    click.echo(f"Saved data for company_id {company_id} to {csv_file}")
                except Exception as e:
                    logging.error(f"Failed to save data for company_id {company_id} to {csv_file}: {e}")
                    continue  # Proceed to the next company even if one fails
            else:
                logging.warning(f"No insights returned for company_id: {company_id}")
            # Track total processing time for the company
            company_end_time = time.time()
            total_company_processing_time = company_end_time - company_start_time

            logging.info(f"Time to get OpenAI response: {openai_response_time:.2f} seconds")
            logging.info(f"Total processing time for company {company_id}: {total_company_processing_time:.2f} seconds")

        ending_time = time.time()
        total_time = ending_time - starting_time  
        
        click.echo("\n=== Insight Analysis Metrics Summary ===")
        click.echo(f"Companies Processed: {company_ids}")
        click.echo(f"Week: {week}")
        click.echo(f"Date: {date_str}")
        click.echo(f'Total time: {total_time}')

    except Exception as e:
        logging.error(f"Error in get_tickets: {e}")
