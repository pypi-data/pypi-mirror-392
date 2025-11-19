from baltra_sdk.legacy.dashboards_folder.models import db, Redemptions, Employees, Prizes
import logging
from typing import List, Dict, Optional
from datetime import datetime, date
from sqlalchemy import func, extract, desc

class RedemptionsManager:
    """
    Class for managing redemption data operations for the React dashboard.
    Provides methods to fetch, format, and update redemption data for a specific company.
    """
    
    def __init__(self, company_id: int = None):
        """
        Initialize the RedemptionsManager class.
        
        Args:
            company_id (int, optional): The ID of the company to fetch redemptions for.
        """
        self.company_id = company_id
        self.db_session = db.session
        self.redemptions_data = None
    
    def fetch_redemptions(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Fetch all redemptions for the specified company with employee information.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            List[Dict]: List of redemptions formatted as dictionaries.
        """
        try:
            # Use the provided company_id or the one from initialization
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided to fetch redemptions")
                return []
            
            # Query for redemptions with employee and prize information
            redemptions = (
                self.db_session.query(
                    Redemptions,
                    Employees.first_name,
                    Employees.last_name,
                    Employees.area,
                    Employees.customer_key,
                    Prizes.nombre.label("prize_name")
                )
                .join(Employees, Redemptions.employee_id == Employees.employee_id)
                .join(Prizes, Redemptions.prize_id == Prizes.prize_id)
                .filter(Redemptions.company_id == target_company_id)
                .order_by(desc(Redemptions.date_requested))
                .all()
            )
            
            logging.info(f"Retrieved {len(redemptions)} redemptions for company_id: {target_company_id}")
            
            # Store the raw data
            self.redemptions_data = redemptions
            
            # Format the data for frontend use
            return self.format_redemptions()
            
        except Exception as e:
            logging.error(f"Error fetching redemptions: {str(e)}")
            logging.error(f"Stack trace: {logging.traceback.format_exc()}")
            return []
    
    def format_redemptions(self) -> List[Dict]:
        """
        Format the redemption data for frontend display.
        
        Returns:
            List[Dict]: List of formatted redemption data.
        """
        if not self.redemptions_data:
            return []
        
        formatted_redemptions = []
        
        for item in self.redemptions_data:
            redemption, first_name, last_name, area, customer_key, prize_name = item 
            
            # Determine status
            status = self._determine_status(redemption)
            
            redemption_data = {
                "id": redemption.redemption_id,
                "employeeName": f"{first_name} {last_name}",
                "employeeArea": area or "Not specified",
                "customerKey": customer_key or "", 
                "prizeName": prize_name,
                "requestDate": redemption.date_requested.isoformat() if redemption.date_requested else None,
                "estimatedDeliveryDate": redemption.estimated_delivery_date.isoformat() if redemption.estimated_delivery_date else None,
                "deliveryDateToCompany": redemption.delivery_date_to_company.isoformat() if redemption.delivery_date_to_company else None,
                "deliveredToCompany": redemption.delivered_to_company,
                "deliveryDateToEmployee": redemption.delivery_date_to_employee.isoformat() if redemption.delivery_date_to_employee else None,
                "deliveredToEmployee": redemption.delivered_to_employee,
                "status": status
            }
            formatted_redemptions.append(redemption_data)
        
        return formatted_redemptions
    
    def _determine_status(self, redemption) -> str:
        """
        Determine the current status of a redemption.
        
        Args:
            redemption: The redemption object
            
        Returns:
            str: Status description
        """
        if redemption.delivered_to_employee:
            return "Delivered to Employee"
        elif redemption.delivered_to_company:
            return "At Company, Pending Delivery to Employee"
        elif redemption.estimated_delivery_date:
            if redemption.estimated_delivery_date > date.today():
                return "On the Way to Company"
            else:
                return "On the Way to Company"
        else:
            return "Processing"
    
    def get_monthly_stats(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Get monthly statistics for claimed and delivered prizes.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            List[Dict]: Monthly statistics
        """
        try:
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided to fetch monthly stats")
                return []
            
            # Get current year
            current_year = datetime.now().year
            
            # Query for monthly stats
            monthly_stats = (
                self.db_session.query(
                    extract('month', Redemptions.date_requested).label('month'),
                    func.count(Redemptions.redemption_id).label('claimed'),
                    func.sum(
                        func.cast(Redemptions.delivered_to_employee == True, db.Integer)
                    ).label('delivered')
                )
                .filter(
                    Redemptions.company_id == target_company_id,
                    extract('year', Redemptions.date_requested) == current_year
                )
                .group_by('month')
                .order_by('month')
                .all()
            )
            
            # Format results
            result = []
            for month_num, claimed, delivered in monthly_stats:
                month_name = datetime(2000, int(month_num), 1).strftime('%B')
                result.append({
                    'month': month_name,
                    'claimed': claimed,
                    'delivered': delivered or 0  # Handle None values
                })
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting monthly stats: {str(e)}")
            logging.error(f"Stack trace: {logging.traceback.format_exc()}")
            return []
    
    def update_redemption_status(self, redemption_id: int, status_type: str) -> bool:
        """
        Update the status of a redemption.
        
        Args:
            redemption_id (int): The ID of the redemption to update
            status_type (str): The type of status to update ('company' or 'employee')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            redemption = self.db_session.query(Redemptions).get(redemption_id)
            
            if not redemption:
                logging.error(f"Redemption with ID {redemption_id} not found")
                return False
            
            today = date.today()
            
            if status_type == 'company':
                redemption.delivered_to_company = True
                redemption.delivery_date_to_company = today
                logging.info(f"Marked redemption {redemption_id} as delivered to company")
            elif status_type == 'employee':
                redemption.delivered_to_employee = True
                redemption.delivery_date_to_employee = today
                logging.info(f"Marked redemption {redemption_id} as delivered to employee")
            else:
                logging.error(f"Invalid status type: {status_type}")
                return False
            
            self.db_session.commit()
            return True
            
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error updating redemption status: {str(e)}")
            return False
    
    def get_redemptions_for_company(self, company_id: Optional[int] = None) -> Dict:
        """
        Get all redemptions for a company with additional metadata.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            Dict: Dictionary with redemptions data and metadata.
        """
        target_company_id = company_id if company_id is not None else self.company_id
        
        redemptions = self.fetch_redemptions(target_company_id)
        monthly_stats = self.get_monthly_stats(target_company_id)
        
        result = {
            "success": True,
            "count": len(redemptions),
            "data": redemptions,
            "monthlyStats": monthly_stats
        }
        
        return result
