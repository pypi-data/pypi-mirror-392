import json
import logging
from itertools import islice
from baltra_sdk.shared.utils.postgreSQL_utils import get_unique_employee_ids_points, get_messages_for_batch_rewards, store_flag
from baltra_sdk.shared.utils.openai_assistant import get_openai_client
from flask import current_app
from datetime import datetime, timedelta
from openai import OpenAI, AssistantEventHandler, APITimeoutError
from typing_extensions import override


"""
File description:

This file is used as a framework to have multiple OpenAI assistants scan all conversations (one-by-one)
periodically during off-peak chatbot hours in order to raise red flags and store them in a table 
called flagged_conversations in the database.
After conversations are flagged a customer support person can review more carefully each one of the 
flagged conversations.

Assistants output needs to be configured in OpenAI as a json-object with the following format:

{
  "interactions": [
    {
      "assistant_id": "assistant_name",
      "employee_id": "12345",
      "company_id": "5",
      "action": "canje",
      "requested_reward": "licuadora", #This field can be empty
      "justification": "El colaborador solicitó canjear puntos por una licuadora."
    },
    {
      "assistant_id": "rewards_assistant",
      "employee_id": "11111",
      "company_id": "2222",
      "action": "canje",
      "requested_reward": "tarjeta de regalo walmart", #This field can be empty
      "justification": "El colaborador solicitó explícitamente la tarjeta de Walmart."
    }
  ]
}

In case assistants detect no conversations to flag they should return
{
  "interactions": []
}

Current active assistants:
asst_i7twclPZzkFo5EtmKD4NzpGf - red_flag_assistant_rewards - Detect rewards request
asst_RgtadihryrDYSq48aaXQWzSE - red_flag_assistant_frustration - Detect general frustration or complaints

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

# Review conversation context using multiple assistants
def review_conversation_context(conversation_data, client, assistant_ids):
    """
    Sends conversation data to multiple OpenAI assistants for contextual review.

    Args:
        conversation_data: List of tuples containing employee_id, sent_by, and message.
        client: The OpenAI client instance.
        assistant_ids: A list of assistant IDs to review the conversation.

    Returns:
        A list of flagged results from the assistants.
    """
    try:
        # Format input data as a single string
        input_data = "\n".join([f"{emp_id}, {cmp_id}, {sent_by}, {msg}" 
                                for emp_id, cmp_id, sent_by, msg in conversation_data])
        

        # Create a new thread for the conversation
        thread = client.beta.threads.create()
        
        # Add the formatted data to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=input_data
        )
        
        # Collect results from multiple assistants
        all_results = []
        for assistant_id in assistant_ids:
            # Run the assistant and wait for the result
            run = client.beta.threads.runs.create_and_poll(
                assistant_id=assistant_id,
                thread_id=thread.id
            )
            
            # Retrieve the results
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            response = messages.data[0].content[0].text.value
            handler = EventHandler()
            with client.beta.threads.runs.stream(
                assistant_id=assistant_id,
                thread_id=thread.id,
                event_handler=handler,
            ) as stream:
                stream.until_done()

            messages = client.beta.threads.messages.list(thread_id=thread.id)
            response = handler.full_text  # buffered full response from EventHandler


            # Parse and store the results
            all_results.append(json.loads(response))
        
        return all_results
    
    except Exception as e:
        logging.error(f"Error in review_conversation_context: {e}")
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

# Process employee conversations in batches for review
def process_conversations(start_date, assistant_ids):
    """
    Processes employee conversations in batches and sends them for contextual review.

    Args:
        start_date: The start date of the period to process.
        batch_size: The number of employees to process in each batch.
        assistant_ids: A list of assistant IDs to use for review.

    Returns:
        A list of all flagged results across all batches.
    """
    client = get_openai_client()
    
    # Fetch all unique employee IDs for the company
    all_employee_ids = get_unique_employee_ids_points(start_date)
    logging.info(f'Procesing {len(all_employee_ids)} conversations')
    
    # Split the employee IDs into batches
    batches = chunked_iterable(all_employee_ids, size=1)
    all_results = []

    for batch in batches:
        logging.debug(f"Processing batch: {batch}")
        
        # Fetch messages for the current batch of employees
        conversation_data = get_messages_for_batch_rewards(batch, start_date=start_date)
        
        # Review the conversation data using multiple assistants
        batch_results = review_conversation_context(conversation_data, client, assistant_ids)
        
        # Collect flagged results if available
        all_results.extend(batch_results)
        
    return all_results

# Main function to get flagged results from all conversations
def get_flagged_conversations(start_date, assistant_ids):
    """
    Retrieves flagged interactions from all conversations within a given time range.

    Steps:
    1. Calls `process_conversations` to fetch flagged conversations based on `start_date` and `assistant_ids`.
    2. If results are available, iterates through them to extract individual flagged interactions.
    3. Flattens the interactions into a single list for easier processing.
    4. Returns the flattened list of flagged interactions.
    5. Logs a warning if no results are found and handles any exceptions gracefully.

    Args:
    start_date (str): The starting date to filter conversations.
    assistant_ids (list): A list of assistant IDs to filter the conversations.

    Returns:
    list: A flattened list of flagged interactions or an empty list if no results are found.
    """

    try:
        all_results = process_conversations(start_date, assistant_ids)
        
        # Return results if available
        if all_results:
            flattened_data = []
            for result in all_results:
                interactions = result['interactions']
                if interactions:  # If there are interactions
                    for interaction in interactions:
                        flattened_data.append(interaction)
            return flattened_data
        else:
            logging.warning("No results to process")
            return []
    except Exception as e:
        logging.error(f"Error in get_flagged_conversations: {e}")
        return []


def run_flagged_conversations(current_app):
    """
    Fetches and processes flagged conversations from the past 7 days.

    Steps:
    1. Defines the assistant IDs to filter conversations.
    2. Calculates the `start_date` as 7 days before the current date.
    3. Calls `get_flagged_conversations` to retrieve flagged conversations.
    4. Iterates over each flagged conversation:
    - Logs the flagged conversation.
    - Stores the flagged conversation using `store_flag`.

    Returns:
        None
    """
    with current_app.app_context():
        #assistant_ids = ['asst_i7twclPZzkFo5EtmKD4NzpGf', 'asst_RgtadihryrDYSq48aaXQWzSE']
        assistant_ids = ['asst_RgtadihryrDYSq48aaXQWzSE']
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        flagged_conversations = get_flagged_conversations(start_date, assistant_ids)
        for conversation in flagged_conversations:
            logging.info(f'Flagged Conversation: {conversation}')
            store_flag(conversation)

