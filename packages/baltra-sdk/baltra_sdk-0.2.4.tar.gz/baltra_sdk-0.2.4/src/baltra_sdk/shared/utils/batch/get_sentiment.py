import pandas as pd
import json
import logging
from itertools import islice
from baltra_sdk.shared.utils.postgreSQL_utils import get_unique_employee_ids, get_messages_for_batch, store_sentiment_data
from baltra_sdk.shared.utils.openai_assistant import get_openai_client
from flask import current_app
import click  # Add this import at the top with other imports
from openai import OpenAI, AssistantEventHandler, APITimeoutError
from typing_extensions import override


"""
Module for processing employee conversations to extract sentiment. 
Extracts numeric values for pulse survey questions for each company to a CSV file. This is triggered from
a flask command.

Functions:
- `chunked_iterable(iterable, size)`: Split iterable into chunks.
- `classify_conversation_data(conversation_data, client, assistant_id)`: Classify messages via OpenAI assistant.
- `process_batches(company_id, batch_size)`: Process employee messages in batches.
- `json_to_csv(all_results, company_id, date, week)`: Convert classification results to CSV.
- `get_sentiment(company_id, week, date)`: Main function to analyze sentiment and save results.
"""

# Split iterable into chunks
def chunked_iterable(iterable, size):
    """
    Splits an iterable into chunks of a specified size.
    
    Args:
        iterable: The iterable to chunk.
        size: The maximum size of each chunk.
    
    Returns:
        An iterator of tuples, each containing `size` elements.
    """
    iterator = iter(iterable)
    return iter(lambda: tuple(islice(iterator, size)), ())

# Classify conversation data
def classify_conversation_data(conversation_data, client, assistant_id):
    """
    Sends conversation data to the OpenAI assistant for classification.

    Args:
        conversation_data: List of tuples containing employee_id, sent_by, and message.
        client: The OpenAI client instance.
        assistant_id: The ID of the OpenAI assistant.

    Returns:
        A JSON object with the assistant's classification results.
    """
    try:
        # Format input data as a single string
        input_data = "\n".join([f"{emp_id}, {sent_by}, {msg}" 
                                for emp_id, sent_by, msg in conversation_data])
        # Create a new thread
        thread = client.beta.threads.create()
        # Add the formatted data to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=input_data
        )
        handler = EventHandler()
        with client.beta.threads.runs.stream(
            assistant_id=assistant_id,
            thread_id=thread.id,
            event_handler=handler,
        ) as stream:
            stream.until_done()

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = handler.full_text  # buffered full response from EventHandler

        # Parse the assistant's response
        return json.loads(response)
    except Exception as e:
        logging.error(f"Error in classify_conversation_data: {e}")
        return []

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
def process_batches(company_id, batch_size=5):
    """
    Processes employee messages in batches and sends them to the assistant for classification.

    Args:
        company_id: The ID of the company for which messages are processed.
        batch_size: The number of employees to process in each batch.

    Returns:
        A list of all classification results across all batches.
    """
    assistant_id = 'asst_O8kxbU8sPE5jsZm6KyjKbVTy'
    client = get_openai_client()
    # Fetch all unique employee IDs for the company
    all_employee_ids = get_unique_employee_ids(company_id, 7)
    # Split the employee IDs into batches
    batches = chunked_iterable(all_employee_ids, batch_size)
    all_results = []

    for batch in batches:
        logging.info(f"Processing batch: {batch}")
        # Fetch messages for the current batch of employees
        conversation_data = get_messages_for_batch(batch, company_id, 7)
        # Classify the conversation data using the assistant
        batch_results = classify_conversation_data(conversation_data, client, assistant_id)
        # Collect responses if available
        if 'responses' in batch_results:
            all_results.extend(batch_results['responses'])
        else:
            logging.warning(f"No responses found for batch: {batch}")
    return all_results

def process_sentiment_metrics(all_results, company_id, date, week):
    """
    Processes classification results to extract data quality metrics and returns processed DataFrame.
    This function handles the core data processing that can be used for both metrics and CSV generation.

    Args:
        all_results: The list of classification results.
        company_id: The company ID associated with the data.
        date: The date for which the data is being processed.
        week: The week number for the data.

    Returns:
        tuple: (processed_df, metrics_dict) where:
            - processed_df is the processed pandas DataFrame
            - metrics_dict contains the calculated metrics
    """
    try:
        # Convert to DataFrame for easier analysis
        df = pd.json_normalize(all_results)
        
        # Scale the score to a 0-10 range and handle empty values
        df['score'] = pd.to_numeric(df['score'], errors='coerce') * 2
        
        # Add additional context fields
        df['company_id'] = company_id
        df['date'] = date
        df['week'] = week

        # app/constants/sentiment_questions.py
        CATEGORY_QUESTIONS = {
            "work environment": "¿Qué tanto recomendarías a un amigo o familiar trabajar en esta empresa?",
            "communication with manager": "¿Qué tan frecuente recibes reconocimiento positivo por tu trabajo?",
            "motivation": "¿Qué tan feliz estás en tu trabajo?"
        }
        # Map metric to question
        df['question'] = df['metric'].map(CATEGORY_QUESTIONS)

        # Final column selection
        df = df[['employee_id', 'company_id', 'date', 'week', 'metric', 'score', 'question']]


        # Calculate metrics
        total_records = len(df)
        distinct_employees = df['employee_id'].nunique()
        
        # Group by employee_id and count null scores
        null_scores_by_employee = df.groupby('employee_id')['score'].apply(
            lambda x: x.isnull().sum()
        ).value_counts().to_dict()
        
        # Initialize counts for 0,1,2,3 null scores
        employees_with_nulls = {
            0: null_scores_by_employee.get(0, 0),
            1: null_scores_by_employee.get(1, 0),
            2: null_scores_by_employee.get(2, 0),
            3: null_scores_by_employee.get(3, 0)
        }
        
        # Calculate completion rate
        total_not_null = df['score'].notna().sum()
        completion_rate = total_not_null / total_records if total_records > 0 else 0

        # Prepare metrics dictionary
        metrics = {
            'company_id': company_id,
            'date': date,
            'week': week,
            'total_records': total_records,
            'distinct_employees': distinct_employees,
            'employees_with_nulls': employees_with_nulls,
            'completion_rate': completion_rate
        }
        
        # Log the metrics
        logging.info(f"Data Quality Metrics for company {company_id}:")
        logging.info(f"Total records: {total_records}")
        logging.info(f"Distinct employees: {distinct_employees}")
        logging.info("Employees by number of null scores:")
        for nulls, count in employees_with_nulls.items():
            logging.info(f"  {nulls} null scores: {count} employees")
        logging.info(f"Completion rate: {completion_rate:.2%}")

        return df, metrics
        
    except Exception as e:
        logging.error(f"Error in process_sentiment_metrics: {e}")
        return None, None

def json_to_csv(all_results, company_id, date, week):
    """
    Converts classification results to a CSV file.

    Args:
        all_results: The list of classification results.
        company_id: The company ID associated with the data.
        date: The date for which the data is being processed.
        week: The week number for the data.

    Returns:
        None
    """
    try:
        # Use process_sentiment_metrics to get the processed DataFrame
        df, _ = process_sentiment_metrics(all_results, company_id, date, week)
        
        if df is not None:
            # Save the DataFrame to a CSV file
            csv_file = f'sentiment_company{company_id}_W{week}.csv'
            df.to_csv(csv_file, index=False)
            logging.info(f"Data successfully saved to {csv_file}")
        else:
            logging.error("Failed to process data for CSV conversion")
            
    except Exception as e:
        logging.error(f"Error in json_to_csv: {e}")

# Main function
def get_sentiment(company_id, week, date):
    """
    Orchestrates the sentiment analysis process:
    - Processes messages in batches
    - Classifies messages using the assistant
    - Displays metrics and asks for user confirmation
    - Stores results in database if user confirms

    Args:
        company_id: The ID of the company for which sentiment is being analyzed
        week: The week number for the data
        date: The date for which sentiment is being analyzed

    Returns:
        None
    """
    try:
        # Process employee messages and classify sentiment
        all_results = process_batches(company_id)
        
        if not all_results:
            logging.warning(f"No results to process for company {company_id}")
            return
            
        # Process data and get both DataFrame and metrics
        df, metrics = process_sentiment_metrics(all_results, company_id, date, week)
        
        if df is None or metrics is None:
            logging.error("Failed to process sentiment data")
            return

        # Display metrics summary
        click.echo("\n=== Sentiment Analysis Metrics Summary ===")
        click.echo(f"Company ID: {company_id}")
        click.echo(f"Week: {week}")
        click.echo(f"Date: {date}")
        click.echo(f"Total Records: {metrics['total_records']}")
        click.echo(f"Distinct Employees: {metrics['distinct_employees']}")
        click.echo("Null Score Distribution:")
        for nulls, count in metrics['employees_with_nulls'].items():
            click.echo(f"  Employees with {nulls} null scores: {count}")
        click.echo(f"Completion Rate: {metrics['completion_rate']:.2%}")
        click.echo("=====================================\n")

        # Ask for user confirmation
        if click.confirm('Do you want to proceed with storing these results in the database?', default=True):
            # Convert DataFrame to list of dictionaries for database storage
            processed_data = df.to_dict('records')
            
            # Store data in sentiment table
            if store_sentiment_data(processed_data):
                click.echo(click.style(f"Successfully stored {len(processed_data)} sentiment records for company {company_id}", fg='green'))
            else:
                click.echo(click.style("Failed to store sentiment data in database", fg='red'))
        else:
            click.echo("Storage operation cancelled by user")
            
    except Exception as e:
        logging.error(f"Error in get_sentiment: {e}")
