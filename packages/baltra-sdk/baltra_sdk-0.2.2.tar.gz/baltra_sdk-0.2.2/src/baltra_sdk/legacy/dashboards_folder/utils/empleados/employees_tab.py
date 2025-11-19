from baltra_sdk.legacy.dashboards_folder.models import db, Employees, Points, Rewards
from baltra_sdk.shared.utils.employee_data import Employee
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta, date
from sqlalchemy import func, extract, case, desc, distinct
from calendar import monthrange
import traceback

class EmployeesManager:
    """
    Class for managing employee data operations for the React dashboard.
    Leverages the existing Employee class while providing additional aggregation
    and formatting specifically for the dashboard display.
    """
    
    def __init__(self, company_id: int = None):
        """
        Initialize the EmployeesManager class.
        
        Args:
            company_id (int, optional): The ID of the company to fetch employees for.
        """
        self.company_id = company_id
        self.db_session = db.session
        self.employees_data = None
    
    
    def calculate_lifetime_points(self, employee_id: int) -> int:
        """
        Calculate the total lifetimepoints earned by an employee, excluding redemptions.
        Only counts transactions where transaction = 'points earned'
        
        Args:
            employee_id (int): The ID of the employee
            
        Returns:
            int: Total points earned (excluding redemptions or other transactions)
        """
        try:
            # Query the database directly for efficiency
            earned_points = (
                self.db_session.query(func.sum(Points.points))
                .filter(
                    Points.employee_id == employee_id,
                    Points.transaction == 'points earned'
                )
                .scalar() or 0
            )
            
            logging.debug(f"Total lifetime earned points for employee {employee_id}: {earned_points}")
            return earned_points
        except Exception as e:
            logging.error(f"Error calculating earned points for employee {employee_id}: {str(e)}")
            return 0
            
    def calculate_previous_month_points(self, employee_id: int) -> int:
        """
        Calculate points earned in the previous month using direct SQL.
        Only counts transactions where transaction = 'points earned'.
        
        Args:
            employee_id (int): The ID of the employee
            
        Returns:
            int: Points earned in the previous month
        """
        try:
            # Get the date range for the previous month
            today = date.today()
            a_month_ago = today - timedelta(days = 30)
           
            # Query for sum of points in previous month with transaction = 'points earned'
            previous_month_points = (
                self.db_session.query(func.sum(Points.points))
                .filter(
                    Points.employee_id == employee_id,
                    Points.transaction == 'points earned',
                    Points.date.between(a_month_ago, today)
                )
                .scalar() or 0
            )
            
            return previous_month_points
        except Exception as e:
            logging.error(f"Error calculating previous month points for employee {employee_id}: {str(e)}")
            logging.error(traceback.format_exc())
            return 0
    
    def calculate_average_monthly_points(self, employee_id: int) -> float:
        """
        Calculate the average monthly points earned using direct SQL.
        Only considers transactions where transaction = 'points earned'.
        
        Args:
            employee_id (int): The ID of the employee
            
        Returns:
            float: Average monthly points based on actual earned points per month
        """
        try:
            # Use SQLAlchemy to group by year and month, then calculate average
            result = (
                self.db_session.query(
                    # Extract year and month from date for grouping
                    func.date_trunc('month', Points.date).label('month'),
                    # Sum points for each month
                    func.sum(Points.points).label('monthly_sum')
                )
                .filter(
                    Points.employee_id == employee_id,
                    Points.transaction == 'points earned'
                )
                .group_by(func.date_trunc('month', Points.date))
                .all()
            )
            
            # If no data, return 0
            if not result:
                return 0
                
            # Calculate average of monthly sums
            monthly_sums = [month_sum for _, month_sum in result]
            average = sum(monthly_sums) / len(monthly_sums)
            
            return round(average)
            
        except Exception as e:
            logging.error(f"Error calculating average monthly points for employee {employee_id}: {str(e)}")
            logging.error(traceback.format_exc())  # Add stack trace for debugging
            return 0
    
    def get_monthly_performance(self, employee_id: int, is_current_month: bool = True) -> List[Dict]:
        """
        Get an employee's performance data for the current or previous month.
        
        Args:
            employee_id (int): The ID of the employee
            is_current_month (bool): If True, get current month; if False, get previous month
            
        Returns:
            List[Dict]: List of performance metrics
        """
        try:
            # Calculate the date range
            today = date.today()
            
            if is_current_month:
                # Current month date range
                start_date = date(today.year, today.month, 1)
                end_date = today
            else:
                # Previous month date range
                first_day_previous_month = date(today.year, today.month, 1) - timedelta(days=1)
                start_date = date(first_day_previous_month.year, first_day_previous_month.month, 1)
                last_day_of_month = monthrange(start_date.year, start_date.month)[1]
                end_date = date(start_date.year, start_date.month, last_day_of_month)
            
            # Query for performance metrics in the specified date range
            performance_data = (
                self.db_session.query(
                    Rewards.metric,
                    Rewards.date,
                    Rewards.score,
                    Rewards.weekday
                )
                .filter(
                    Rewards.employee_id == employee_id,
                    Rewards.date.between(start_date, end_date),
                    Rewards.metric == 'asistencia' or Rewards.metric == 'puntualidad'
                )
                .order_by(Rewards.date)
                .all()
            )
            
            # Format the results
            result = []
            for metric, date_val, score, weekday in performance_data:
                result.append({
                    "metric": metric,
                    "date": date_val.isoformat() if date_val else None,
                    "score": score,
                    "weekday": weekday
                })
            
            # Combine all info into the f-string
            #logging.info(f"Monthly performance for employee {employee_id} (Current Month: {is_current_month}): {result}")
            
            return result
        except Exception as e:
            logging.error(f"Error getting monthly performance for employee {employee_id}: {str(e)}")
            return []
    
    def fetch_employees_basic(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Fetch basic employee data for the initial ranking screen.
        Only includes essential fields for the employee ranking table.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            List[Dict]: List of basic employee data formatted as dictionaries.
        """
        try:
            # Use the provided company_id or the one from initialization
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided to fetch employees")
                return []
            
            # Query for active employees in the company
            employees = (
                self.db_session.query(Employees)
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.active == True, 
                    Employees.role != 'Business Owner'
                )
                .order_by(Employees.first_name)
                .all()
            )
            
            logging.info(f"Retrieved {len(employees)} active employees for company_id: {target_company_id}")
            
            # Format only the basic data needed for ranking
            formatted_employees = []
            
            for emp in employees:
                # Calculate earned points directly - more efficient
                total_points = self.calculate_lifetime_points(emp.employee_id)
                
                # Get only the required points stats
                prev_month_points = self.calculate_previous_month_points(emp.employee_id)
                avg_monthly_points = self.calculate_average_monthly_points(emp.employee_id)
                
                # Format with minimal data
                basic_data = {
                    "employee_id": emp.employee_id,
                    "first_name": emp.first_name,
                    "last_name": emp.last_name,
                    "area": emp.area,
                    "sub_area": emp.sub_area,
                    "shift": emp.shift,
                    "birth_date": emp.birth_date,
                    "role": emp.role,
                    "customer_key": emp.customer_key,
                    "points_stats": {
                        "total": total_points,
                        "previous_month": prev_month_points,
                        "monthly_average": avg_monthly_points
                    }
                }
                
                formatted_employees.append(basic_data)
            
            return formatted_employees
            
        except Exception as e:
            logging.error(f"Error fetching basic employees data: {str(e)}")
            return []

    def fetch_employees_directory(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Fetch employee data for the directory view.
        Includes more fields than basic view but still omits detailed performance data.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization.
            
        Returns:
            List[Dict]: List of employee directory data formatted as dictionaries.
        """
        try:
            # Use the provided company_id or the one from initialization
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided to fetch employees")
                return []
            
            # Query for active employees in the company
            employees = (
                self.db_session.query(Employees)
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.active == True, 
                    Employees.role != 'Business Owner'
                )
                .order_by(Employees.first_name)
                .all()
            )
            
            logging.info(f"Retrieved {len(employees)} active employees for directory view, company_id: {target_company_id}")
            
            # Format directory data
            formatted_employees = []
            
            for emp in employees:
                # Create an Employee instance to use its methods
                employee = Employee()
                employee.employee_info = emp
                
                # Calculate total points only
                employee.calculate_total_points()
                total_points = employee.total_points
                
                # Format the start_date
                start_date_formatted = emp.start_date.isoformat() if emp.start_date else None
                
                # Format with directory data
                directory_data = {
                    "employee_id": emp.employee_id,
                    "first_name": emp.first_name,
                    "last_name": emp.last_name,
                    "area": emp.area,
                    "sub_area": emp.sub_area,
                    "shift": emp.shift,
                    "birth_date": emp.birth_date,
                    "role": emp.role,
                    "customer_key": emp.customer_key,
                    "wa_id": emp.wa_id,
                    "total_points": total_points,
                    "start_date": start_date_formatted
                }
                
                formatted_employees.append(directory_data)
            
            return formatted_employees
            
        except Exception as e:
            logging.error(f"Error fetching directory employees data: {str(e)}")
            return []

    def fetch_employee_details(self, employee_id: int) -> Dict:
        """
        Fetch detailed data for a single employee.
        Includes all performance metrics, points history, etc.
        
        Args:
            employee_id (int): The ID of the employee to fetch details for.
            
        Returns:
            Dict: Detailed employee data formatted as a dictionary.
        """
        try:
            # Query for the specific employee
            emp = self.db_session.query(Employees).get(employee_id)
            
            if not emp:
                logging.error(f"Employee with ID {employee_id} not found")
                return {}
            
            # Create an Employee instance to use its methods
            employee = Employee()
            employee.employee_info = emp
            
            current_points = employee.calculate_total_points()
            # Get points data using our optimized methods
            total_points = self.calculate_lifetime_points(employee_id)
            points_array = self.fetch_employee_details_points(employee_id)
            
            # Get performance data
            current_month_performance = self.get_monthly_performance(emp.employee_id, is_current_month=True)
            previous_month_performance = self.get_monthly_performance(emp.employee_id, is_current_month=False)
            
            # Format the start_date
            start_date_formatted = emp.start_date.isoformat() if emp.start_date else None
            
            # Create the detailed employee data
            emp_data = {
                "employee_id": emp.employee_id,
                "first_name": emp.first_name,
                "last_name": emp.last_name,
                "wa_id": emp.wa_id,
                "company_id": emp.company_id,
                "area": emp.area,
                "sub_area": emp.sub_area,
                "role": emp.role,
                "shift": emp.shift,
                "current_points": current_points,
                "start_date": start_date_formatted,
                "active": emp.active,
                "points": points_array,
                "total_lifetime_points": total_points,
                "performance": {
                    "current_month": current_month_performance,
                    "previous_month": previous_month_performance
                }
            }
            
            return emp_data
            
        except Exception as e:
            logging.error(f"Error fetching detailed employee data for ID {employee_id}: {str(e)}")
            return {}
    
    def fetch_employee_details_points(self, employee_id: int) -> List[Dict]:
        """
        Fetch all points entries for an employee using direct SQL.
        Only includes transactions where transaction = 'points earned'.
        Maps metric names according to business rules.
        
        Args:
            employee_id (int): The ID of the employee
            
        Returns:
            List[Dict]: List of formatted points entries
        """
        try:
            # Query for points where transaction = 'points earned'
            points_data = (
                self.db_session.query(
                    Points.date,
                    Points.transaction,
                    Points.points,
                    Points.metric
                )
                .filter(
                    Points.employee_id == employee_id,
                    Points.transaction == 'points earned'
                )
                .order_by(Points.date.desc())
                .all()
            )
            
            # Format the results with metric mapping
            result = []
            for date_val, transaction, points, metric in points_data:
                # Map metric according to rules
                if metric == "puntualidad_asistencia" or metric == "encuesta":
                    mapped_metric = metric
                else:
                    mapped_metric = "desempeño"
                    
                result.append({
                    "date": date_val.isoformat() if date_val else None,
                    "transaction": transaction or "",
                    "points": points or 0,
                    "metric": mapped_metric or ""
                })
            
            return result
        except Exception as e:
            logging.error(f"Error fetching points for employee {employee_id}: {str(e)}")
            logging.error(traceback.format_exc())
            return []
    
    def add_new_employee(self, employee_data: Dict) -> Dict:
        """
        Adds a new employee to the database.

        Args:
            employee_data (Dict): A dictionary containing the new employee's details.
                                  Expected keys: 'first_name', 'last_name', 'role', 'area',
                                                 'sub_area', 'wa_id', 'birth_date', 'start_date'.

        Returns:
            Dict: A dictionary indicating success status and the new employee's ID or an error message.
        """
        try:
            start_date_obj = None
            birth_date_obj = None

            # --- Date Parsing (assuming 'YYYY-MM-DD' format) ---
            start_date_str = employee_data.get('start_date')
            if start_date_str:
                try:
                    start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    logging.error(f"Invalid start_date format: {start_date_str}. Expected YYYY-MM-DD.")
                    return {'success': False, 'error': f"Invalid start_date format: {start_date_str}. Expected YYYY-MM-DD."}

            birth_date_str = employee_data.get('birth_date')
            if birth_date_str:
                try:
                    birth_date_obj = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError:
                    logging.error(f"Invalid birth_date format: {birth_date_str}. Expected YYYY-MM-DD.")
                    # Non-critical, proceed without birth date if format is wrong, but log it.
                    birth_date_obj = None 

            # --- Create new Employee object ---
            new_employee = Employees(
                company_id=self.company_id, # Use company_id from the manager instance
                first_name=employee_data.get('first_name'),
                last_name=employee_data.get('last_name'),
                wa_id=employee_data.get('wa_id'),
                area=employee_data.get('area'),
                role=employee_data.get('role'),
                sub_area=employee_data.get('sub_area'), # Already mapped in API if needed
                shift=employee_data.get('shift'),
                start_date=start_date_obj,
                birth_date=birth_date_obj,
                customer_key=employee_data.get('customer_key'),
                active=True, # Default new employees to active
                left_company=False, # Default new employees have not left
                # Other fields like context, paths, shift, customer_key, end_date are left as default/null
            )

            # --- Add to session and commit ---
            self.db_session.add(new_employee)
            self.db_session.commit()

            logging.info(f"Successfully added new employee with ID: {new_employee.employee_id} for company {self.company_id}")
            return {'success': True, 'employee_id': new_employee.employee_id}

        except Exception as e:
            self.db_session.rollback() # Rollback transaction on error
            error_msg = f"Database error adding employee for company {self.company_id}: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            return {'success': False, 'error': 'Database error occurred while adding employee.'}
    
    def update_employee_details(self, employee_id: int, update_data: Dict) -> Dict:
        """
        Updates specific details for an existing employee.

        Args:
            employee_id (int): The ID of the employee to update.
            update_data (Dict): A dictionary containing the fields to update.
                                  Allowed keys: 'role', 'area', 'sub_area', 'wa_id',
                                                'active', 'left_company', 'shift'.

        Returns:
            Dict: A dictionary indicating success status or an error message.
        """
        try:
            employee = self.db_session.query(Employees).get(employee_id)

            if not employee:
                logging.error(f"Attempted to update non-existent employee with ID: {employee_id}")
                return {'success': False, 'error': f'Employee with ID {employee_id} not found.'}

            allowed_fields = {'role', 'area', 'sub_area', 'wa_id', 'active', 'left_company', 'shift'}
            updated = False

            for key, value in update_data.items():
                if key in allowed_fields:
                    # Special handling for active/left_company logic
                    if key == 'active' and value is False:
                        if employee.active is True: # Only update if changing from True to False
                            setattr(employee, 'active', False)
                            setattr(employee, 'left_company', True)
                            logging.info(f"Updated employee {employee_id}: active set to False, left_company set to True.")
                            updated = True
                        # If trying to set active=False but it's already False, do nothing for this field
                        # but allow left_company to be potentially updated separately if provided.
                    elif key == 'left_company':
                         # Allow explicitly setting left_company, potentially overriding the active=False logic
                         # if left_company=False is passed *after* active=False.
                         if getattr(employee, key) != value:
                            setattr(employee, key, value)
                            logging.info(f"Updated employee {employee_id}: {key} set to {value}.")
                            updated = True
                    elif getattr(employee, key) != value:
                        setattr(employee, key, value)
                        logging.info(f"Updated employee {employee_id}: {key} set to {value}.")
                        updated = True
                else:
                    logging.warning(f"Attempted to update disallowed field '{key}' for employee {employee_id}")

            if updated:
                self.db_session.commit()
                logging.info(f"Successfully committed updates for employee ID: {employee_id}")
                return {'success': True, 'message': 'Employee updated successfully.'}
            else:
                logging.info(f"No changes detected for employee ID: {employee_id}")
                return {'success': True, 'message': 'No changes detected.'}

        except Exception as e:
            self.db_session.rollback()
            error_msg = f"Database error updating employee {employee_id}: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            return {'success': False, 'error': 'Database error occurred while updating employee.'}
    
    
    
   