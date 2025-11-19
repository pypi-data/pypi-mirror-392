from baltra_sdk.legacy.dashboards_folder.models import db, Employees, Companies, Rewards, Points, CompanyAreas, Prizes, Messages, Redemptions
from baltra_sdk.shared.utils.date_utils import get_latest_sunday_datetime
import logging
from datetime import datetime, timedelta, date
from flask import current_app

"""
This module defines the Employee class and its associated methods to interact with the 
employee-related data within the database. It provides functionalities such as:
- Fetching employee data from the database
- Retrieving company details based on the employee's company_id
- Fetching performance, rewards, points, and redemptions data
- Calculating the total points earned by the employee
- Formatting and structuring rewards and redemption information for presentation
- Managing the employee's conversational context and interactions with the assistant

The Employee class interacts with several database tables, such as:
- Employees (holds basic employee information)
- Companies (holds company-related details)
- Rewards (stores performance data for the employee)
- Points (tracks the employee's accumulated points)
- Redemptions (stores the redemption history for prizes)
- Prizes (contains prize information available for redemption)
- CompanyAreas (provides details of areas and sub-areas within the company)

Dependencies:
- SQLAlchemy ORM for database interaction
- Logging for error handling and data tracking
- datetime and timedelta for managing date and time operations
- Flask's current_app config for dynamic configuration settings

"""

class Employee:
    """
    This class represents an employee and provides various methods to interact with the 
    employee's data, calculate their performance and points, and manage rewards and redemptions.

    Key Responsibilities:
    - Fetch and store employee-related data (e.g., basic information, company details, 
      performance metrics, rewards points, redemptions, etc.).
    - Calculate the total points earned by the employee based on rewards and points history.
    - Format and display the rewards, prizes, and redemption history in a readable format for 
      integration with other systems (e.g., AI-powered assistants).
    - Manage employee-specific conversation details for communication purposes.
    - Interact with the company's data and area-specific rewards description.

    Attributes:
    - wa_id (str): WhatsApp ID of the employee.
    - db_session (SQLAlchemy Session): Session for interacting with the database.
    - client (object): The client responsible for API calls or external interactions.
    - wa_id_system (str): System-specific WhatsApp ID for the employee.
    - employee_info (Employee): Data fetched from the Employees table.
    - company_info (Company): Data fetched from the Companies table.
    - rewards_info (list): Data on the employee's performance metrics from the Rewards table.
    - points_info (list): History of points earned by the employee from the Points table.
    - area_info (CompanyArea): Data on the employee's area from the CompanyAreas table.
    - prizes_info (list): Data on available prizes for the employee to redeem.
    - total_points (int): Total points accumulated by the employee.
    - conversation_info (ConversationInfo): Information related to the employee's conversation with the assistant.
    - redemptions_info (list): List of prizes the employee has redeemed.
    """
    def __init__(self, wa_id=None, client=None, wa_id_system=None):
        self.wa_id = wa_id
        self.db_session = db.session  # SQLAlchemy session
        self.client = client
        self.wa_id_system = wa_id_system #Not needed anymore, can delete
        self.employee_info = None #Data fetched from the employees table
        self.company_info = None #Data fetched from the companies table
        self.rewards_info = None #Attendance and puntuality fetched from the rewards table
        self.points_info = None #Points history from the ledger in points table
        self.area_info   = None #Area information from company_areas
        self.prizes_info = None #Prizes from the prizes table
        self.total_points = None #Initialize variable with total points
        self.conversation_info = None #Initialize conversation information
        self.redemptions_info = None #Prizes redeemed from redemptions table
        
    def fetch_employee_data(self):
        """Fetch employee data from the database, prioritizing the smallest company_id."""
        self.employee_info = self.db_session.query(Employees).filter(Employees.wa_id == self.wa_id).order_by(Employees.company_id).first()
        if not self.employee_info:
            self.insert_employee()
            self.employee_info = self.db_session.query(Employees).filter(Employees.wa_id == self.wa_id).order_by(Employees.company_id).first()


    def fetch_company_details(self):
        """Fetch and store company details in self.company_info."""
        if not self.employee_info:
            self.fetch_employee_data()

        self.company_info = (
            self.db_session.query(Companies)
            .filter_by(company_id=self.employee_info.company_id)
            .first()
        )

        if not self.company_info:
            logging.warning(f"Company details not found for company_id: {self.employee_info.company_id}")

    def fetch_redemptions(self):
        """Fetch and store redemption details for a given employee."""
        if not self.employee_info:
            self.fetch_employee_data()

        cutoff_date = datetime.now() - timedelta(days=current_app.config["REDEMPTIONS_CUTOFF"])

        self.redemptions_info = (
            self.db_session.query(Redemptions)
            .filter_by(employee_id=self.employee_info.employee_id)
            .filter(Redemptions.estimated_delivery_date >= cutoff_date)
            .all()
        )

        if not self.redemptions_info:
            logging.debug(f"No redemptions found for employee_id: {self.employee_info.employee_id}")

    def format_redemptions(self):
        """Structure the fetched redemption data into a readable format for the AI agent."""
        if self.redemptions_info is None:
            self.fetch_redemptions()

        if self.prizes_info is None:  # Ensure prizes info is fetched
            self.fetch_prizes()

        structured_redemptions = []

        for redemption in self.redemptions_info or []:
            # Find the corresponding prize from self.prizes_info
            prize = next((p for p in self.prizes_info if p.prize_id == redemption.prize_id), None)

            structured_data = {
                "prize_name": prize.nombre if prize else "Unknown",
                "points_deducted": prize.puntos if prize else None,
                "date_requested": redemption.date_requested,
                "estimated_delivery_date": redemption.estimated_delivery_date,
                "delivered_to_employee": redemption.delivered_to_employee,
                "delivery_date_to_employee": redemption.delivery_date_to_employee,
                "status": self.get_redemption_status(redemption),
                "prize_description": prize.description if prize else None,
            }

            structured_redemptions.append(structured_data)
        return structured_redemptions

    def get_redemption_status(self, redemption):
        """Determine the current status of a redemption."""
        if redemption.delivered_to_employee:
            return "Delivered to Employee"
        elif redemption.estimated_delivery_date:
            return f"Estimated Delivery: {redemption.estimated_delivery_date}"
        else:
            return "Processing"

    def fetch_performance(self):
        """Fetch performance data for the employee within the cutoff period."""
        if not self.employee_info:
            self.fetch_employee_data()

        cutoff_date = datetime.now() - timedelta(weeks=current_app.config["REWARDS_CUTOFF"])

        self.rewards_info = (
            self.db_session.query(Rewards.metric, Rewards.date, Rewards.score, Rewards.weekday)
            .filter(Rewards.employee_id == self.employee_info.employee_id, Rewards.date >= cutoff_date)
            .all()
        )

        return [{"metric": r.metric, "date": str(r.date), "score": r.score, "weekday": r.weekday} for r in self.rewards_info]
    

    def fetch_points(self, employee_id = None):
        """Fetch points data for the employee."""
        if not self.employee_info:
            self.fetch_employee_data()

        if employee_id is None:
            employee_id = self.employee_info.employee_id

        # Store full points data in self.points_info
        self.points_info = (
            self.db_session.query(Points)
            .filter(Points.employee_id == employee_id)
            .all()
        )

        # Return only the required fields
        return [{
            "date": p.date.isoformat() if p.date else None,
            "week": p.week,
            "transaction": p.transaction,
            "points": p.points,
            "metric": p.metric
        } for p in self.points_info]

    def calculate_total_points(self, employee_id=None):
        """Calculate the total points for the employee."""
        # Fetch points data only if it hasn't been fetched yet
        if employee_id is None:
            employee_id = self.employee_info.employee_id    
        points = self.fetch_points(employee_id)  # Fetch the points data

        logging.debug(f'Points: {points}')
        # Sum up the points and return the total
        self.total_points = sum(p['points'] for p in points)
        return self.total_points
    
    def format_points_cutoff(self, employee_id = None):
        if not self.points_info:
            self.fetch_points(employee_id)

        cutoff_date = datetime.now().date() - timedelta(weeks=current_app.config["REWARDS_CUTOFF"])

        return [{
            "date": p.date.isoformat() if p.date else None,
            "week": p.week,
            "transaction": p.transaction,
            "points": p.points,
            "metric": p.metric
        } for p in self.points_info if p.date and p.date >= cutoff_date]

    def fetch_area_details(self):
        """Fetch area details (rewards description) for the employee's sub_area."""
        if not self.employee_info:
            self.fetch_employee_data()

        self.area_info = (
            self.db_session.query(CompanyAreas)
            .filter_by(company_id=self.employee_info.company_id, area_name=self.employee_info.sub_area)
            .first()
        )

    def fetch_prizes(self, company_id=None):
        """
        Fetch prizes from the database and store them in self.prizes_info.

        Args:
            company_id: ID of the company (optional)

        """
        try:
            if company_id is None:
                company_id = self.employee_info.company_id

            self.prizes_info = (
                self.db_session.query(Prizes)
                .filter_by(company_id=company_id, active=True)
                .order_by(Prizes.puntos.asc())
                .all()
            )

        except Exception as e:
            logging.error(f"Error fetching prizes: {e}")
            self.prizes_info = []

    def format_prizes(self):
        """
        Process stored prize information and format it for display.

        Returns:
            dict: Dictionary with prize details formatted for display, or None if no prizes exist.
        """
        if not self.prizes_info:
            self.fetch_prizes()
        if not self.employee_info:
            self.fetch_employee_data()
        
        result = {}

        today = date.today()
        employee_start_date = self.employee_info.start_date
        days_in_company = (today - employee_start_date).days if employee_start_date else 0

        for i, prize in enumerate(self.prizes_info, 1):
            has_enough_points = self.total_points >= prize.puntos  # Check if employee can afford prize
            has_enough_tenure = days_in_company >= prize.min_days_in_company #Check if the employee has the required tenure to redeem prize

            is_available = has_enough_points and has_enough_tenure

            result[f"premio_{i}"] = prize.nombre
            result[f"puntos_{i}"] = prize.puntos
            result[f"desc_{i}"] = prize.description
            result[f"boolean_{i}"] = is_available
            result[f"link_{i}"] = prize.link
            result[f"image_{i}"] = ""  # Initialize empty image field

            logging.debug(f"Prize {i} details - Name: {prize.nombre}, Points: {prize.puntos}, Description: {prize.description}, Available: {is_available}")

        return result    

    def format_prizes_legacy(self, company_id=None):
        """
        Helper function to format the prizes data into the required structure.
        
        Returns:
            list: List of formatted prize data with title, points, and image_url.
        """
        rewards = []
        
        if not self.prizes_info:
            self.fetch_prizes(company_id=company_id)
        
        for prize in self.prizes_info:
            reward = {
                "title": prize.nombre,
                "points": prize.puntos,
                "image_url": prize.link
            }
            rewards.append(reward)
        
        return rewards

    def get_thread_id(self, conversation_type):
        """Get or create a thread ID based on previous messages using SQLAlchemy."""
        # Query to check for previous messages using SQLAlchemy
        result = (
            self.db_session.query(Messages.thread_id, Messages.time_stamp)
            .filter_by(wa_id=self.wa_id, conversation_type=conversation_type)
            .order_by(Messages.time_stamp.desc())
            .first()
        )

        # If result exists, check the timestamp and decide
        if result:
            thread_id, time_stamp = result
            logging.debug(f'Thread_ID: {thread_id} - Timstamp: {time_stamp}')
            cutoff = get_latest_sunday_datetime()
            logging.debug(f'time_stamp {time_stamp} > cutoff: {cutoff}')
            if time_stamp > cutoff:
                # If the latest thread was used within the last week, return the thread_id
                return thread_id
            else:
                # If the latest thread was not used within the last week, create a new thread
                try:
                    thread = self.client.beta.threads.create()
                    logging.debug(f'New Thread Cutoff: {thread.id}')
                    return thread.id
                except Exception as e:
                    logging.error(f"Error creating thread: {e}")
                    return None  # Or handle as appropriate
        else:
            # If no thread exists, create a new thread
            try:
                thread = self.client.beta.threads.create()
                logging.debug(f'New Thread No Thread found: {thread.id}')
                return thread.id
            except Exception as e:
                logging.error(f"Error creating thread: {e}")
                return None # Or handle as appropriate

    def fetch_conversation_info(self):
        """Fetch the conversation type and assistant ID, and store them in self.conversation_info."""
        if not self.company_info:
            logging.warning("Company details are not available in self.company_info.")
            return

        if not self.employee_info:
            self.fetch_employee_data()

        role = getattr(self.employee_info, "role", "Unknown")

        # Determine conversation type
        conversation_type = "owner" if role == 'Business Owner' else "employee"

        # Select assistant ID based on conversation type
        assistant_id = self.company_info.owner_assistant_id if conversation_type == "owner" else self.company_info.employee_assistant_id
        
        #get thread id
        thread_id = self.get_thread_id(conversation_type)

        # Store the data in self.conversation_info as an instance of ConversationInfo
        self.conversation_info = ConversationInfo(conversation_type, assistant_id, thread_id)

    def insert_employee(self):
        """Insert a new employee into the database."""
        try:
            # Create a new employee object with default values
            new_employee = Employees(
                wa_id=self.wa_id,
                first_name="unknown",
                last_name="unknown",
                company_id=9999,  # Assuming company_id=9999 as default
                area="unknown",
                role="unknown"
            )
            self.db_session.add(new_employee)
            self.db_session.commit()  # Commit to save the new employee
            
            # Retrieve the employee_id and company_id
            employee_id = new_employee.employee_id
            company_id = new_employee.company_id

            # Log the insertion with employee_id and company_id
            logging.info(f"{self.wa_id} not found in employees database. Stored in employees database as: unknown with employee_id: {employee_id} and company_id: {company_id}")
            
            return new_employee
        except Exception as e:
            logging.error(f"Unexpected error inserting employee {self.wa_id}: {e}")
            return None
        
    def get_latest_prizes_as_strings(self):
        """
        Return cinepolis, soriana, and recargas gift card folios as single strings
        by concatenating the list of folios from latest_prizes JSON field.
        """
        if not self.employee_info:
            self.fetch_employee_data()

        result = {}
        json_data = getattr(self.employee_info, "latest_prizes", {}) or {}

        for prize_key in ["cinepolis", "soriana", "recargas"]:
            values = json_data.get(prize_key, [])
            if isinstance(values, list):
                result[prize_key] = ", ".join(values)
            elif isinstance(values, str):
                result[prize_key] = values
            else:
                result[prize_key] = ""

        return result


    def sanitize_data(self, data):
        """Cleans data to ensure json.dumps won't crash"""
        
        if isinstance(data, dict):
            return {k: self.sanitize_data(v) for k, v in data.items() if v is not None}
        
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        
        elif isinstance(data, (datetime, date)):
            return data.isoformat()  # Convierte fechas a string ISO 8601
        
        elif isinstance(data, (int, float, str, bool)):
            return data  # Mantiene valores seguros
        
        else:
            return str(data)  # Convierte cualquier otro tipo a string para evitar errores

    def create_employee_data(self):
        """Create an employee data dictionary from fetched values, logging warnings for missing data."""
        
        # Ensure required data is fetched before proceeding
        if not self.employee_info:
            self.fetch_employee_data()

        if not self.company_info:
            self.fetch_company_details()

        if not self.conversation_info:
            self.fetch_conversation_info()

        if not self.points_info:
            self.fetch_points()

        if not self.total_points:
            self.calculate_total_points()

        if not self.rewards_info:
            self.fetch_performance()

        if not self.prizes_info:
            self.fetch_prizes()

        if not self.area_info:
            self.fetch_area_details()

        if not self.redemptions_info:
            self.fetch_redemptions()

        if not self.conversation_info:
            self.fetch_conversation_info()

        # Construct the dictionary with safe default values
        data = {
            "employee_id": getattr(self.employee_info, "employee_id", "Unknown"),
            "first_name": getattr(self.employee_info, "first_name", "Unknown"),
            "last_name": getattr(self.employee_info, "last_name", "Unknown"),
            "wa_id": getattr(self, "wa_id", "Unknown"),
            "company_id": getattr(self.employee_info, "company_id", "Unknown"),
            "company_name": getattr(self.company_info, "company_name", "Unknown"),
            "area": getattr(self.employee_info, "area", "Unknown"),
            "sub_area": getattr(self.employee_info, "sub_area", "Unknown"),
            "role": getattr(self.employee_info, "role", "Unknown"),
            "context": getattr(self.employee_info, "context", None) or "Unknown",
            "rewards_description": getattr(self.area_info, "rewards_description", "No rewards description"),
            "thread_id": getattr(self.conversation_info, "thread_id", "Unknown"),
            "conversation_type": getattr(self.conversation_info, "conversation_type", "Unknown"),
            "assistant_id": getattr(self.conversation_info, "assistant_id", "Unknown"),
            "start_date": getattr(self.employee_info, "start_date", "Unknown"),
            "active": getattr(self.employee_info, "active", "Unknown"),
            "total_points": self.total_points if self.total_points is not None else 0,
            "rewards": self.format_prizes_legacy() or [],
            "prizes": self.format_prizes() or {},
            "performance": self.fetch_performance() or [],
            "points": self.fetch_points() or [],
            "points_cutoff": self.format_points_cutoff() or [],
            "weekly_path": getattr(self.employee_info, "weekly_path", ""),
            "monthly_path": getattr(self.employee_info, "monthly_path", ""),
            "daily_path": getattr(self.employee_info, "daily_path", ""),
            "rewards_path": getattr(self.employee_info, "rewards_path", ""),
            "current_date": (datetime.now() + timedelta(hours=-6)).isoformat(),
            "redemptions": self.format_redemptions() or [],
            **self.get_latest_prizes_as_strings(),
        }

        # Check final dictionary for missing key values and log warnings
        for key, value in data.items():
            if value in ["Unknown", None, [], {}]:  # Identify problematic defaults
                logging.info(f"Missing or default value for '{key}': {value}")

        return self.sanitize_data(data)

class ConversationInfo:
    """
    Create a class for conversation related attributes such as type (owner or employee), assistant_id and thread id
    attributes from OpenAI.
    """
    def __init__(self, conversation_type=None, assistant_id=None, thread_id = None):
        self.conversation_type = conversation_type
        self.assistant_id = assistant_id
        self.thread_id = thread_id

