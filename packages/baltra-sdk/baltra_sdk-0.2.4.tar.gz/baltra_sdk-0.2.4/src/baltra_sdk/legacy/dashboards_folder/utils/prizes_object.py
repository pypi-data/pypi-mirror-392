from baltra_sdk.legacy.dashboards_folder.models import db, Prizes
import logging
from typing import List, Dict, Optional

class PrizeManager:
    """
    Class for managing prize data operations for the React dashboard.
    Provides methods to fetch and format prize data for a specific company.
    """
    
    def __init__(self, company_id: int = None):
        """
        Initialize the Prize manager class.
        
        Args:
            company_id (int, optional): The ID of the company to fetch prizes for.
        """
        self.company_id = company_id
        self.db_session = db.session
        self.prizes_data = None
    
    def fetch_prizes(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Fetch all prizes for the specified company.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            List[Dict]: List of prizes formatted as dictionaries.
        """
        try:
            # Use the provided company_id or the one from initialization
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided to fetch prizes")
                return []
            
            # Query for active prizes for the company
            prizes = (
                self.db_session.query(Prizes)
                #.filter_by(company_id=target_company_id, active=True)
                .filter_by(company_id=target_company_id)
                .order_by(Prizes.puntos.asc())
                .all()
            )
            
            logging.info(f"Retrieved {len(prizes)} prizes for company_id: {target_company_id}")
            
            # Store the raw data
            self.prizes_data = prizes
            
            # Format the data for frontend use
            return self.format_prizes()
            
        except Exception as e:
            logging.error(f"Error fetching prizes: {str(e)}")
            return []
    
    def format_prizes(self) -> List[Dict]:
        """
        Format the prize data for frontend display.
        
        Returns:
            List[Dict]: List of formatted prize data.
        """
        if not self.prizes_data:
            return []
        
        formatted_prizes = []
        
        for prize in self.prizes_data:
            prize_data = {
                "name": prize.nombre,
                "points": prize.puntos,
                "price": prize.precio,
                "description": prize.description,
                "imageUrl": prize.link,
                "active": prize.active
            }
            formatted_prizes.append(prize_data)
        
        return formatted_prizes
    
    def get_prizes_for_company(self, company_id: Optional[int] = None) -> Dict:
        """
        Get all prizes for a company with additional metadata.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            Dict: Dictionary with prizes data and metadata.
        """
        target_company_id = company_id if company_id is not None else self.company_id
        
        prizes = self.fetch_prizes(target_company_id)
        
        result = {
            "success": True,
            "count": len(prizes),
            "data": prizes
        }
        
        return result
