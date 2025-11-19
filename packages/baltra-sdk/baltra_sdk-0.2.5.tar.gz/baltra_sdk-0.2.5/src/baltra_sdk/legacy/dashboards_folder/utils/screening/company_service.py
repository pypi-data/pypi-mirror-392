from collections import defaultdict
import logging
from sqlalchemy import exc
from baltra_sdk.legacy.dashboards_folder.models import CompaniesScreening, db
from typing import List, Dict
from datetime import date
from baltra_sdk.shared.utils.screening.google_maps import LocationService

logger = logging.getLogger(__name__)

class CompanyScreeningService:
    """Manager of area performance metrics with integrated error handling"""
    
    def __init__(self, company_id: int):
        if not isinstance(company_id, int) or company_id <= 0:
            raise ValueError("Invalid company ID")
            
        self.company_id = company_id
        
        
    def company_to_dict(self, company: CompaniesScreening) -> dict:
        return {
            "company_id": company.company_id,
            "name": company.name,
            "latitude": company.latitude,
            "longitude": company.longitude,
            "address": company.address,
            "interview_excluded_dates": company.interview_excluded_dates,
            "interview_days": company.interview_days,
            "maps_link_json": company.maps_link_json,
            "interview_hours": company.interview_hours,
            "benefits": company.benefits,
            "website": company.website,
            "description": company.description,
            "interview_address_json": company.interview_address_json,
            "general_faq": self.parse_company_FAQs(company.general_faq),
            "phone": company.phone,
            "interview_addresses": self.parse_company_maps_links_and_addresses(company.maps_link_json, company.interview_address_json),
            "group_id": company.group_id,
        }
        
        
    def edit_company(self, company: dict) -> bool:
        """Edits a company in the database"""
        try:
            c = CompaniesScreening.query.filter_by(
                company_id=self.company_id
            ).first()
            
            if not c:
                raise ValueError(f"Company with ID {self.company_id} not found")
            
            if company.get("name") is not None:
              c.name = company.get("name")
            
            if company.get("latitude") is not None:
              c.latitude = company.get("latitude")
            
            if company.get("longitude") is not None:
              c.longitude = company.get("longitude")
            
            if company.get("address") is not None:
              c.address = company.get("address")
            
            if company.get("interview_excluded_dates") is not None:
              c.interview_excluded_dates = company.get("interview_excluded_dates")
            
            if company.get("interview_days") is not None:
              c.interview_days = company.get("interview_days")

            if company.get("maps_link_json") is not None:
              c.maps_link_json = company.get("maps_link_json")
            
            if company.get("interview_hours") is not None:
              c.interview_hours = company.get("interview_hours")
            
            if company.get("benefits") is not None:
              c.benefits = company.get("benefits")
            
            if company.get("website") is not None:
              c.website = company.get("website")
            
            if company.get("description") is not None:
              c.description = company.get("description")
              
            if company.get("interview_addresses") is not None:
              self.overwrite_maps_links_and_addresses(company.get("interview_addresses"))
            
            db.session.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error editing company: {str(e)}")
            return False

    def get_company(self) -> dict:
        """Retrieves company data from the database"""
        
        try:
            company = CompaniesScreening.query.filter_by(
                company_id=self.company_id
            ).distinct().first()
            
            return self.company_to_dict(company) if company else None
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching company_screening: {str(e)}")
            raise RuntimeError("Error retrieving company_screening from database")

    def add_excluded_dates(self, dates: List[date]) -> bool:
        """Adds dates to the interview_excluded_dates field"""
        try:
            company = CompaniesScreening.query.filter_by(
                company_id=self.company_id
            ).first()
            
            if not company:
                raise ValueError(f"Company with ID {self.company_id} not found")
            
            if not company.interview_excluded_dates:
                company.interview_excluded_dates = []

            for d in dates:
                if d not in company.interview_excluded_dates:
                    company.interview_excluded_dates.append(d)
            
            db.session.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error adding excluded dates: {str(e)}")
            return False
          
    def remove_excluded_dates(self, dates: List[date]) -> bool:
        """Removes dates from the interview_excluded_dates field"""
        try:
            company = CompaniesScreening.query.filter_by(
                company_id=self.company_id
            ).first()
            
            if not company:
                raise ValueError(f"Company with ID {self.company_id} not found")
            
            if not company.interview_excluded_dates:
                return True 
            
            company.interview_excluded_dates = [
                d for d in company.interview_excluded_dates if d not in dates
            ]
            
            db.session.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error removing excluded dates: {str(e)}")
            return False
          
    def add_interview_days(self, days: List[str]) -> bool:
        """Adds days to the interview_days field, ensuring no duplicates."""
        valid_days = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
        
        days = [day for day in days if day in valid_days]
        
        if not days:
            return False  

        try:
            company = CompaniesScreening.query.filter_by(
                company_id=self.company_id
            ).first()
            
            if not company:
                raise ValueError(f"Company with ID {self.company_id} not found")
            
            if not company.interview_days:
                company.interview_days = []
            
            for day in days:
                if day not in company.interview_days:
                    company.interview_days.append(day)
            
            db.session.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error adding interview days: {str(e)}")
            return False


    def remove_interview_days(self, days: List[str]) -> bool:
        """Removes days from the interview_days field."""
        valid_days = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
        
        days = [day for day in days if day in valid_days]
        
        if not days:
            logger.warning("No valid days provided")
            raise ValueError("No valid days provided")

        try:
            company = CompaniesScreening.query.filter_by(
                company_id=self.company_id
            ).first()
            
            if not company:
                raise ValueError(f"Company with ID {self.company_id} not found")
            
            if not company.interview_days:
                return True
            
            company.interview_days = [
                day for day in company.interview_days if day not in days
            ]
            
            db.session.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error removing interview days: {str(e)}")
            return False

    def add_interview_hours(self, hours: List[str]) -> bool:
        """Adds hours to the interview_hours field, ensuring no duplicates."""
        try:
            company = CompaniesScreening.query.filter_by(
                company_id=self.company_id
            ).first()
            
            if not company:
                raise ValueError(f"Company with ID {self.company_id} not found")
            
            if not company.interview_hours:
                company.interview_hours = []

            for hour in hours:
                if hour not in company.interview_hours:
                    company.interview_hours.append(hour)
            
            db.session.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error adding interview hours: {str(e)}")
            return False


    def remove_interview_hours(self, hours: List[str]) -> bool:
        """Removes hours from the interview_hours field."""
        try:
            company = CompaniesScreening.query.filter_by(
                company_id=self.company_id
            ).first()
            
            if not company:
                raise ValueError(f"Company with ID {self.company_id} not found")
            
            if not company.interview_hours:
                return True
            
            company.interview_hours = [
                hour for hour in company.interview_hours if hour not in hours
            ]
            
            db.session.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            logger.error(f"Error removing interview hours: {str(e)}")
            return False

    def add_faq(self, question: str, answer: str):
        """Agrega una nueva pregunta y respuesta al role_info"""
        role = CompaniesScreening.query.filter_by(company_id=self.company_id).first()
        if not role:
            raise ValueError("Role not found")

        info = role.role_info or {}
        count = len([k for k in info if k.startswith("Q")]) + 1

        info[f"Q{count}"] = question
        info[f"A{count}"] = answer

        role.role_info = info
        db.session.commit()

    def edit_faq(self, index: int, question: str, answer: str):
        """Edita una pregunta y respuesta específica"""
        company = CompaniesScreening.query.filter_by(company_id=self.company_id).first()
        if not company:
            raise ValueError("Role not found")

        info = company.general_faq or {}

        q_key = f"Q{index}"
        a_key = f"A{index}"

        if q_key in info and a_key in info:
            info[q_key] = question
            info[a_key] = answer
            company.general_faq = info
            db.session.commit()
        else:
            raise KeyError("FAQ index not found")

    def delete_faq(self, index: int):
        """Elimina una pregunta/respuesta y reordena los índices"""
        company = CompaniesScreening.query.filter_by(company_id=self.company_id).first()
        if not company:
            raise ValueError("Role not found")

        info = company.general_faq or {}
        q_key = f"Q{index}"
        a_key = f"A{index}"

        if q_key not in info or a_key not in info:
            raise KeyError("FAQ index not found")

        # Eliminar la pregunta y respuesta
        del info[q_key]
        del info[a_key]

        # Reorganizar los índices
        faqs = self.parse_company_FAQs(info)
        reordered = {}
        for i, faq in enumerate(faqs, 1):
            reordered[f"Q{i}"] = faq["question"]
            reordered[f"A{i}"] = faq["answer"]

        company.general_faq = reordered
        db.session.commit()

    def overwrite_faqs(self, faqs: List[Dict[str, str]]) -> None:
        """
        Reemplaza completamente las FAQs actuales de un rol.
        """
        company = CompaniesScreening.query.filter_by(company_id=self.company_id).first()
        if not company:
            raise ValueError("Role not found")

        new_info = {}
        for i, faq in enumerate(faqs, start=1):
            new_info[f"Q{i}"] = faq["question"]
            new_info[f"A{i}"] = faq["answer"]

        company.general_faq = new_info
        db.session.commit()
        
        return True
      
    def overwrite_maps_links_and_addresses(self, links: List[str]) -> None:
      
      if not links:
        return True
      
      try:
        locationService = LocationService()
        location_links = []
        addresses = []
        for link in links:
          location = locationService.get_geolocation(link)
          if location:
            location_id = location["id"]
            address = location["address"]
            
            if not location_id or not address:
              logger.warning(f"No location ID or address found for link: {link}")
              continue
            
            link = f"https://www.google.com/maps/place/?q=place_id:{location_id}"
            
            location_links.append(link)
            addresses.append(address)
            
          else:
            logger.warning(f"No location found for link: {link}")
      
        self.overwrite_maps_links(location_links)
        self.overwrite_interview_addresses(addresses)
        
        return True
        
      except Exception as e:
        logger.error(f"Error overwriting maps links and addresses: {e}")
      
    def overwrite_maps_links(self, links: List[str]) -> None:
        """
        Reemplaza completamente las FAQs actuales de un rol.
        """
        company = CompaniesScreening.query.filter_by(company_id=self.company_id).first()
        if not company:
            raise ValueError("Role not found")
        
        new_info = {}
        for i, link in enumerate(links, start=1):
            new_info[f"location_link_{i}"] = link
            
        company.maps_link_json = new_info
        db.session.commit()
        
        return True
      
    def overwrite_interview_addresses(self, addresses:  List[str]) -> None:
        """
        Reemplaza completamente las FAQs actuales de un rol.
        """
        company = CompaniesScreening.query.filter_by(company_id=self.company_id).first()
        if not company:
            raise ValueError("Role not found")
        
        new_info = {}
        for i, address in enumerate(addresses, start=1):
            new_info[f"location_{i}"] = address
        
        
        company.interview_address_json = new_info
        db.session.commit()
        
        return True
      
    def parse_company_maps_links_and_addresses(self, maps_json: dict, addresses_json: dict) -> List[Dict[str, str]]:
      """
      Transforma JSONs de maps_links y interview_addresses en una lista de objetos combinados.
      """
      if maps_json is None:
        maps_json = {}
      if addresses_json is None:
        addresses_json = {}
      
      if not isinstance(maps_json, dict):
        maps_json = {}
      if not isinstance(addresses_json, dict):
        addresses_json = {}
      
      combined_data = []
      
      # Obtener todas las claves de ubicación únicas
      all_location_keys = set()
      for key in maps_json.keys():
        if key.startswith("location_link_"):
          location_num = key.replace("location_link_", "")
          all_location_keys.add(location_num)
      
      for key in addresses_json.keys():
        if key.startswith("location_"):
          location_num = key.replace("location_", "")
          all_location_keys.add(location_num)
      
      # Crear objetos combinados para cada ubicación
      for location_num in sorted(all_location_keys, key=lambda x: int(x) if x.isdigit() else 0):
        map_key = f"location_link_{location_num}"
        address_key = f"location_{location_num}"
        
        combined_data.append({
          "location_id": location_num,
          "map_link": maps_json.get(map_key),
          "address": addresses_json.get(address_key)
        })
      
      return combined_data

    def parse_company_FAQs(self, info_json: dict) -> List[Dict[str, str]]:
        """
        Transforma un JSON de role_info en una lista de objetos {question, answer}.
        """
        if info_json is None:
            return []
        
        if not isinstance(info_json, dict):
            return []

        faqs = []
        q_keys = sorted([k for k in info_json if k.startswith("Q")], key=lambda x: int(x[1:]))
        for q_key in q_keys:
            index = q_key[1:]
            a_key = f"A{index}"
            question = info_json.get(q_key)
            answer = info_json.get(a_key)
            if question is not None and answer is not None:
                faqs.append({
                    "question": question,
                    "answer": answer,
                    "index": index
                })
                              
        return faqs
