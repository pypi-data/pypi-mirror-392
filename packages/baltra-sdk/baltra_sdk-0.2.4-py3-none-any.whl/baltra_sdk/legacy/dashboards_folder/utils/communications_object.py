from baltra_sdk.legacy.dashboards_folder.models import db, ScheduledMessages, WhatsappStatusUpdates, Messages
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, extract, case, desc, literal, text
import traceback

class CommunicationsManager:
    """
    Class for managing communications data operations for the React dashboard.
    Provides methods to fetch and format scheduled messages and their delivery statistics.
    """
    
    def __init__(self, company_id: int = None):
        """
        Initialize the CommunicationsManager class.
        
        Args:
            company_id (int, optional): The ID of the company to fetch communications for.
        """
        self.company_id = company_id
        self.db_session = db.session
        self.messages_data = None
    
    def fetch_scheduled_messages(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Fetch all scheduled messages for the specified company.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            List[Dict]: List of scheduled messages formatted as dictionaries.
        """
        try:
            # Use the provided company_id or the one from initialization
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided to fetch scheduled messages")
                return []
            
            # Query for scheduled messages
            messages = (
                self.db_session.query(ScheduledMessages)
                .filter(ScheduledMessages.company_id == target_company_id)
                .order_by(desc(ScheduledMessages.send_time))
                .all()
            )
            
            logging.info(f"Retrieved {len(messages)} scheduled messages for company_id: {target_company_id}")
            
            # Store the raw data
            self.messages_data = messages
            
            # Format the data for frontend use
            return self.format_messages()
            
        except Exception as e:
            logging.error(f"Error fetching scheduled messages: {str(e)}")
            logging.error(f"Stack trace: {logging.traceback.format_exc()}")
            return []
    
    def format_messages(self) -> List[Dict]:
        """
        Format the scheduled messages data for frontend display.
        
        Returns:
            List[Dict]: List of formatted message data.
        """
        if not self.messages_data:
            return []
        
        formatted_messages = []
        
        for message in self.messages_data:
            message_data = {
                "id": message.id,
                "company_id": message.company_id,
                "template": message.template,
                "send_time": message.send_time.isoformat() if message.send_time else None,
                "recurring_interval": message.recurring_interval,
                "parameters": message.parameters,
                "status": message.status,
                "sender": message.sender,
                "template_content": "{temporary placeholder}",  # Placeholder for now
                "areas": "Todas",  # Default value
               
            }
            formatted_messages.append(message_data)
        
        return formatted_messages
    
    def get_message_history(self, message_id: int) -> List[Dict]:
        """
        Get delivery history for a specific scheduled message.
        
        Args:
            message_id (int): The ID of the scheduled message
            
        Returns:
            List[Dict]: List of historical delivery data
        """
        try:
            # First get the message details to construct the campaign_id pattern
            message = self.db_session.query(ScheduledMessages).get(message_id)
            if not message:
                logging.error(f"Message with ID {message_id} not found")
                return []
                
            # Construct the campaign_id pattern: "company_id-template"
            campaign_id_pattern = f"{message.company_id}-{message.template}"
            logging.info(f"Looking for WhatsApp status updates with campaign_id like: {campaign_id_pattern}%")
            
            # First, get all status_ids that are associated with this campaign
            # The 'posted' status records contain both campaign_id and status_id
            posted_records = (
                self.db_session.query(
                    WhatsappStatusUpdates.status_id,
                    func.date(func.to_timestamp(WhatsappStatusUpdates.timestamp)).label("date")
                )
                .filter(
                    WhatsappStatusUpdates.campaign_id.like(f"{campaign_id_pattern}%"),
                    WhatsappStatusUpdates.status == 'posted'
                )
                .all()
            )
            
            logging.info(f"Found {len(posted_records)} posted messages for campaign {campaign_id_pattern}")
            
            if not posted_records:
                logging.info(f"No posted messages found for campaign {campaign_id_pattern}")
                # Return default entry with zeros
                return [{
                    "date": message.send_time.date().isoformat() if message.send_time else datetime.now().date().isoformat(),
                    "programmed": 0,
                    "posted": 0,
                    "failed": 0,
                    "sent": 0,
                    "delivered": 0,
                    "read": 0,
                    "status": "Programado" if message.send_time and message.send_time > datetime.now() else "Sin datos"
                }]
            
            # Group status_ids by date to calculate per-day statistics
            dates_and_status_ids = {}
            for status_id, date in posted_records:
                if date not in dates_and_status_ids:
                    dates_and_status_ids[date] = []
                dates_and_status_ids[date].append(status_id)
            
            # For each date, calculate message stats
            result = []
            for date, status_ids in sorted(dates_and_status_ids.items(), key=lambda x: x[0], reverse=True):
                # Count how many messages were posted (should equal len(status_ids))
                posted_count = len(status_ids)
                
                # Now count sent, delivered, and read statuses for these status_ids
                status_counts = (
                    self.db_session.query(
                        WhatsappStatusUpdates.status,
                        func.count(func.distinct(WhatsappStatusUpdates.status_id)).label("count")
                    )
                    .filter(
                        WhatsappStatusUpdates.status_id.in_(status_ids),
                        WhatsappStatusUpdates.status.in_(['failed', 'sent', 'delivered', 'read'])
                    )
                    .group_by(WhatsappStatusUpdates.status)
                    .all()
                )
                
                # Initialize counters
                sent_count = 0
                delivered_count = 0
                read_count = 0
                failed_count = 0
                
                # Process the counts
                for status, count in status_counts:
                    if status == 'sent':
                        sent_count = count
                    elif status == 'delivered':
                        delivered_count = count
                    elif status == 'read':
                        read_count = count
                    elif status == 'failed':
                        failed_count = count
                
                # Determine overall status
                if failed_count > 0 and failed_count >= (posted_count - failed_count):
                    status = "Fallido"
                elif read_count > 0:
                    status = "Enviado"
                elif delivered_count > 0:
                    status = "Enviado"
                elif sent_count > 0:
                    status = "Enviado"
                else:
                    status = "Programado"
                
                # Add entry to result
                result.append({
                    "date": date.isoformat() if date else None,
                    "programmed": posted_count,
                    "posted": posted_count,
                    "failed": failed_count,
                    "sent": sent_count,
                    "delivered": delivered_count,
                    "read": read_count,
                    "status": status
                })
            
            return result
        
        except Exception as e:
            logging.error(f"Error getting message history: {str(e)}")
            logging.error(traceback.format_exc())
            return []
    
    
    def get_weekly_message_stats(self) -> Dict:
        """
        Calculate message statistics for the company over a series of weeks.
        Returns weekly metrics from the oldest message date up to current date, 
        capped at 52 weeks maximum.
        
        Returns:
            Dict: Contains weekly series of message statistics with format:
                {
                    'success': bool,
                    'data': List[{
                        'date': str,  # ISO format date
                        'total_messages': int,
                        'unique_employees': int,
                        'avg_messages_per_employee': float,
                        'week_start': str,  # ISO format date
                        'week_end': str,  # ISO format date
                    }]
                }
        """
        try:
            if self.company_id is None:
                logging.error("No company ID provided to fetch message statistics")
                return {
                    'success': False,
                    'error': 'No company ID provided',
                    'data': []
                }
            
            # Get the oldest message date for this company
            oldest_message = (
                self.db_session.query(
                    func.min(Messages.time_stamp)
                )
                .filter(Messages.company_id == self.company_id)
                .scalar()
            )
            
            if not oldest_message:
                logging.info(f"No messages found for company_id: {self.company_id}")
                return {
                    'success': True,
                    'data': []
                }
            
            # Calculate weeks between oldest message and today
            today = datetime.now().date()
            oldest_date = oldest_message.date()
            total_weeks = (today - oldest_date).days // 7
            
            # Cap at 52 weeks
            weeks_back = min(52, total_weeks)
            
            weekly_metrics = []

            # Calculate metrics for each week
            for week_offset in range(weeks_back):
                # Calculate week boundaries
                analysis_date = today - timedelta(weeks=week_offset)
                week_end = analysis_date
                week_start = analysis_date - timedelta(days=6)  # Get full week
                
                # Query to get message counts and unique employees for this week
                stats = (
                    self.db_session.query(
                        func.count(Messages.message_serial).label('total_messages'),
                        func.count(func.distinct(Messages.employee_id)).label('unique_employees')
                    )
                    .filter(
                        Messages.company_id == self.company_id,
                        Messages.time_stamp >= week_start,
                        Messages.time_stamp < week_end + timedelta(days=1)  # Include full end day
                    )
                    .first()
                )
                
                total_messages = stats.total_messages if stats else 0
                unique_employees = stats.unique_employees if stats else 0
                
                # Calculate average messages per employee
                avg_messages = (
                    float(total_messages) / unique_employees if unique_employees > 0 else 0
                )
                
                # Add metrics for this week
                weekly_metrics.append({
                    'date': week_end.isoformat(),
                    'total_messages': total_messages,
                    'unique_employees': unique_employees,
                    'avg_messages_per_employee': round(avg_messages, 2),
                    'week_start': week_start.isoformat(),
                    'week_end': week_end.isoformat()
                })
            
            logging.info(f"Retrieved weekly message stats for company_id: {self.company_id}, "
                        f"weeks: {weeks_back} (from {oldest_date.isoformat()} to {today.isoformat()})")
            
            return {
                'success': True,
                'data': sorted(weekly_metrics, key=lambda x: x['date'])
            }
            
        except Exception as e:
            logging.error(f"Error calculating message stats: {str(e)}")
            logging.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
