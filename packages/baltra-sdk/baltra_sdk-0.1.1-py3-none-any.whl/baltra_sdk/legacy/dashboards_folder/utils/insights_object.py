from baltra_sdk.legacy.dashboards_folder.models import db, Insights
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy import func, desc

class InsightsManager:
    """
    Class for managing insights data operations for the React dashboard.
    Provides methods to fetch, format, and update insights data for a specific company.
    """
    
    def __init__(self, company_id: int = None):
        """
        Initialize the InsightsManager class.
        
        Args:
            company_id (int, optional): The ID of the company to fetch insights for.
        """
        self.company_id = company_id
        self.db_session = db.session
        self.insights_data = None
    
    def fetch_insights(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Fetch all insights for the specified company.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            List[Dict]: List of insights formatted as dictionaries.
        """
        try:
            # Use the provided company_id or the one from initialization
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided to fetch insights")
                return []
            
            # Query for insights
            insights = (
                self.db_session.query(Insights)
                .filter(Insights.company_id == target_company_id)
                .order_by(desc(Insights.date))
                .all()
            )
            
            logging.info(f"Retrieved {len(insights)} insights for company_id: {target_company_id}")
            
            # Store the raw data
            self.insights_data = insights
            
            # Format the data for frontend use
            return self.format_insights()
            
        except Exception as e:
            logging.error(f"Error fetching insights: {str(e)}")
            logging.error(f"Stack trace: {logging.traceback.format_exc()}")
            return []
    
    def format_insights(self) -> List[Dict]:
        """
        Format the insights data for frontend display.
        
        Returns:
            List[Dict]: List of formatted insight data.
        """
        if not self.insights_data:
            return []
        
        formatted_insights = []
        
        for insight in self.insights_data:
            insight_data = {
                "id": insight.insight_id,
                "date": insight.date.isoformat() if insight.date else None,
                "week": insight.week,
                "category": insight.category,
                "body": insight.body,
                "active": insight.active,
                "area": insight.area,
                "title": insight.title,
                "status": insight.status,
                "frequency": insight.frequency,
                "comment": insight.comment,
                # Determine if this is an operations or HR insight
                "isOperations": insight.assigned_to and "operaciones" in insight.assigned_to.lower(),
                "isHR": insight.assigned_to and "recursos humanos" in insight.assigned_to.lower(),
                "theme": insight.theme
            }
            formatted_insights.append(insight_data)
        
        return formatted_insights
    
    def get_insight_counts(self) -> Dict:
        """
        Get counts of different insight categories.
        
        Returns:
            Dict: Dictionary with various insight counts.
        """
        if not self.insights_data:
            return {
                "total": 0,
                "open": 0,
                "inProgress": 0,
                "closed": 0,
                "operations": 0,
                "hr": 0
            }
        
        # Initialize counters
        total = len(self.insights_data)
        open_count = 0
        in_progress_count = 0
        closed_count = 0
        operations_count = 0
        hr_count = 0
        
        # Count insights by type
        for insight in self.insights_data:
            status = insight.status or " "
            
            if status.lower() == "abierto":
                open_count += 1
            elif status.lower() == "en progreso":
                in_progress_count += 1
            elif status.lower() in ["cerrado", "despriorizado"]:
                closed_count += 1
                
            # Count by area
            if insight.assigned_to and insight.category == 'ticket':
                if "operaciones" in insight.assigned_to.lower():
                    operations_count += 1
                elif "recursos humanos" in insight.assigned_to.lower():
                    hr_count += 1
        
        logging.info(f'Open Count {open_count} / Closed Count {closed_count}')

        return {
            "total": total,
            "open": open_count,
            "inProgress": in_progress_count,
            "closed": closed_count,
            "operations": operations_count,
            "hr": hr_count
        }
    
    def update_insight_status(self, insight_id: int, status: str) -> bool:
        """
        Update the status of an insight.
        
        Args:
            insight_id (int): The ID of the insight to update
            status (str): The new status value
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Validate status value
            valid_statuses = ["abierto", "en progreso", "cerrado", "despriorizado"]
            if status.lower() not in valid_statuses:
                logging.error(f"Invalid status value: {status}")
                return False
            
            insight = self.db_session.query(Insights).get(insight_id)
            
            if not insight:
                logging.error(f"Insight with ID {insight_id} not found")
                return False
            
            # Update the status
            insight.status = status.title()  # Capitalize first letter of each word
            self.db_session.commit()
            
            logging.info(f"Updated status of insight {insight_id} to {status}")
            return True
            
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error updating insight status: {str(e)}")
            return False
    
    def add_insight_comment(self, insight_id: int, comment: str) -> bool:
        """
        Add a comment to an insight.
        
        Args:
            insight_id (int): The ID of the insight to update
            comment (str): The comment to add
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            insight = self.db_session.query(Insights).get(insight_id)
            
            if not insight:
                logging.error(f"Insight with ID {insight_id} not found")
                return False
            
            # Update the comment
            insight.comment = comment
            self.db_session.commit()
            
            logging.info(f"Added comment to insight {insight_id}")
            return True
            
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error adding insight comment: {str(e)}")
            return False
    
    def get_insights_for_company(self, company_id: Optional[int] = None) -> Dict:
        """
        Get all insights for a company with additional metadata.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            Dict: Dictionary with insights data and metadata.
        """
        target_company_id = company_id if company_id is not None else self.company_id
        
        insights = self.fetch_insights(target_company_id)
        counts = self.get_insight_counts()
        
        # Get unique areas and months for filtering
        areas = self._get_unique_areas()
        months = self._get_unique_months()
        
        result = {
            "success": True,
            "count": len(insights),
            "data": insights,
            "stats": counts,
            "filterOptions": {
                "areas": areas,
                "months": months
            }
        }
        
        return result
    
    def _get_unique_areas(self) -> List[str]:
        """
        Get a list of unique areas from the insights data.
        
        Returns:
            List[str]: List of unique area names.
        """
        if not self.insights_data:
            return []
            
        areas = set()
        for insight in self.insights_data:
            if insight.area:
                areas.add(insight.area)
                
        return sorted(list(areas))
    
    def _get_unique_months(self) -> List[Dict]:
        """
        Get a list of unique months from the insights data.
        
        Returns:
            List[Dict]: List of unique months with value and label.
        """
        if not self.insights_data:
            return []
            
        months = set()
        formatted_months = []
        
        for insight in self.insights_data:
            if insight.date:
                month_str = insight.date.strftime('%Y-%m')
                if month_str not in months:
                    months.add(month_str)
                    formatted_months.append({
                        'value': month_str,
                        'label': insight.date.strftime('%B %Y').capitalize()
                    })
                    
        # Sort by date (most recent first)
        formatted_months.sort(key=lambda x: x['value'], reverse=True)
        return formatted_months
