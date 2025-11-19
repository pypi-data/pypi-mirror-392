from baltra_sdk.legacy.dashboards_folder.models import (CompaniesScreening)


def get_company_location(company_id):
    """
    Retrieves the latitude and longitude of a company from the database.

    Args:
    - company_id (int): The ID of the company.

    Returns:
    - dict or None: A dictionary with latitude and longitude if found, None otherwise.
    """
    company = CompaniesScreening.query.with_entities(
        CompaniesScreening.latitude,
        CompaniesScreening.longitude
    ).filter_by(company_id=company_id).first()

    if company and company[0] and company[1]:
        return {
            'latitude': company[0],
            'longitude': company[1]
        }
    
    return None
