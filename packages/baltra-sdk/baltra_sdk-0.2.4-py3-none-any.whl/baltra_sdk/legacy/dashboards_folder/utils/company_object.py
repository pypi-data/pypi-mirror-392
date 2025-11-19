import logging
from baltra_sdk.legacy.dashboards_folder.models import (
    db, Companies)
import traceback

def get_company_info(company_id):
    """Get basic company information."""
    try:
        # Use a safer approach with db.session.query instead of direct model access
        company = db.session.query(Companies).filter_by(company_id=company_id).first()
        if company is None:
            logging.warning(f"No company found with ID: {company_id}")
            return f"Company {company_id}"
        
        company_name = company.company_name
        logging.info(f"Retrieved company name: {company_name}")
        return company_name
    except Exception as e:
        logging.error(f"Error retrieving company info: {str(e)}")
        logging.error(traceback.format_exc())
        return f"Company {company_id}"