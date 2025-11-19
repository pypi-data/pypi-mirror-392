# employees_metrics.py
from baltra_sdk.legacy.dashboards_folder.models import db, Employees
from sqlalchemy import func, desc
from typing import List, Dict, Optional
import logging
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class TenureAnalysisManager:
    """
    Class for managing employee tenure analysis.
    Calculates 6-month retention percentages and turnover rates based on active employees.
    Excludes employees with role 'Business Owner' from the analysis.
    """
    
    def __init__(self, company_id: int = None):
        """
        Initialize the TenureAnalysisManager.
        
        Args:
            company_id (int, optional): The ID of the company to analyze
        """
        self.company_id = company_id
        self.db_session = db.session
        self.TENURE_THRESHOLD = 3  # Fixed 3-month threshold

    def calculate_tenure_metrics(self, company_id: Optional[int] = None) -> Dict:
        """
        Calculate the percentage of active employees with more than 6 months tenure.
        Excludes employees with role 'Business Owner' from the calculation.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization
            
        Returns:
            Dict: Tenure metrics and historical data with weekly granularity
        """
        try:
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided")
                return {
                    'success': False,
                    'error': 'Company ID is required'
                }

            # Get all employees with their start dates, excluding Business Owners
            employees = (
                self.db_session.query(
                    Employees.employee_id,
                    Employees.start_date,
                    Employees.end_date
                )
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.start_date.isnot(None),  # Ensure start_date exists
                    Employees.role != 'Business Owner'  # Exclude Business Owners
                )
                .all()
            )

            if not employees:
                return {
                    'success': True,
                    'data': []
                    } 

            # Calculate metrics for each week in the last year
            today = date.today()
            weekly_metrics = []

            for week_offset in range(52):  # Last 52 weeks
                analysis_date = today - relativedelta(weeks=week_offset)
                metrics = self._calculate_metrics_for_date(employees, analysis_date)
                weekly_metrics.append({
                    'date': analysis_date.strftime('%Y-%m-%d'),  # Using full date for weekly data
                    'total_employees': metrics['total_employees'],
                    'retention_rate': metrics['retention_rate'],
                    'retained_count': metrics['retained_count']
                })

            # Get current metrics
            current_metrics = self._calculate_metrics_for_date(employees, today)

            return {
                'success': True,
                'data':  sorted(weekly_metrics, key=lambda x: x['date'])
            }

        except Exception as e:
            logging.error(f"Error calculating tenure metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_metrics_for_date(self, employees: List, analysis_date: date) -> Dict:
        """
        Calculate 6-month tenure metrics for active employees at a specific date.
        
        Args:
            employees: List of employee records
            analysis_date: Date to calculate metrics for
            
        Returns:
            Dict: Metrics including total employees and retention rate
        """
        total_employees = 0
        retained_count = 0

        for emp in employees:
            # Check if employee was active on analysis date
            # Active means: started before or on analysis date AND
            # either has no end date or ended after analysis date
            if emp.start_date <= analysis_date and (
                emp.end_date is None or emp.end_date >= analysis_date
            ):
                total_employees += 1
                
                # Calculate tenure at analysis date
                tenure_months = (
                    (analysis_date.year - emp.start_date.year) * 12 + 
                    (analysis_date.month - emp.start_date.month)
                )

                # Count employees with 6+ months tenure
                if tenure_months >= self.TENURE_THRESHOLD:
                    retained_count += 1

        # Calculate retention rate
        retention_rate = (
            round((retained_count / total_employees) * 100, 2)
            if total_employees > 0
            else 0
        )

        return {
            'total_employees': total_employees,
            'retention_rate': retention_rate,
            'retained_count': retained_count
        }

    def calculate_turnover_metrics(self, company_id: Optional[int] = None) -> Dict:
        """
        Calculate weekly turnover metrics for the past year.
        Includes both weekly metrics and 4-week moving average for turnover rate.
        Excludes employees with role 'Business Owner' from the calculation.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization
            
        Returns:
            Dict: Turnover metrics with weekly granularity including total employees,
                 employees who left, turnover rate, and 4-week moving average
        """
        try:
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided")
                return {
                    'success': False,
                    'error': 'Company ID is required'
                }

            # Get all employees with their start and end dates, excluding Business Owners
            employees = (
                self.db_session.query(
                    Employees.employee_id,
                    Employees.start_date,
                    Employees.end_date
                )
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.start_date.isnot(None),  # Ensure start_date exists
                    Employees.role != 'Business Owner'  # Exclude Business Owners
                )
                .all()
            )

            if not employees:
                return {
                    'success': True,
                    'data': []
                }

            # Calculate metrics for each week in the last year
            today = date.today()
            weekly_metrics = []

            for week_offset in range(52):  # Last 52 weeks
                analysis_date = today - relativedelta(weeks=week_offset)
                week_end = analysis_date
                week_start = analysis_date - relativedelta(days=6)  # Get full week
                
                metrics = self._calculate_turnover_for_week(employees, week_start, week_end)
                weekly_metrics.append({
                    'date': analysis_date.strftime('%Y-%m-%d'),  # End of week date
                    'total_employees': metrics['total_employees'],
                    'employees_left': metrics['employees_left'],
                    'turnover_rate': 4.3 * metrics['turnover_rate'] # 4.3 * Weekly turnover to convert to monthly
                })

            # Sort metrics by date before calculating moving average
            weekly_metrics = sorted(weekly_metrics, key=lambda x: x['date'])
            
            # Calculate 4-week moving average for turnover rate
            window_size = 4
            for i in range(len(weekly_metrics)):
                # Get the last 4 weeks of data (or less if at the start)
                window_start = max(0, i - window_size + 1)
                window = weekly_metrics[window_start:i + 1]
                
                # Calculate weighted average based on total employees
                total_left = sum(week['employees_left'] for week in window)
                total_emp = sum(week['total_employees'] for week in window)
                
                moving_avg = (
                    round((total_left / total_emp) * 100, 2)
                    if total_emp > 0
                    else 0
                )
                
                weekly_metrics[i]['turnover_rate_ma'] = 4.3 * moving_avg #4.3 * Weekly turnover to convert to monthly

            return {
                'success': True,
                'data': weekly_metrics
            }

        except Exception as e:
            logging.error(f"Error calculating turnover metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_turnover_for_week(self, employees: List, week_start: date, week_end: date) -> Dict:
        """
        Calculate turnover metrics for a specific week.
        
        Args:
            employees: List of employee records
            week_start: Start date of the week
            week_end: End date of the week
            
        Returns:
            Dict: Metrics including total employees, employees who left, and turnover rate
        """
        total_employees = 0
        employees_left = 0

        for emp in employees:
            # Check if employee was active at the start of the week
            if emp.start_date <= week_start:
                if emp.end_date is None or emp.end_date >= week_start:
                    total_employees += 1
                    
                    # Check if employee left during this week
                    if emp.end_date and week_start <= emp.end_date <= week_end:
                        employees_left += 1

        # Calculate weekly turnover rate
        turnover_rate = (
            round((employees_left / total_employees) * 100, 2)
            if total_employees > 0
            else 0
        )

        return {
            'total_employees': total_employees,
            'employees_left': employees_left,
            'turnover_rate': turnover_rate
        }

    def calculate_average_tenure(self, company_id: Optional[int] = None) -> Dict:
        """
        Calculate the average tenure in months for active employees on a weekly basis.
        Excludes employees with role 'Business Owner' from the calculation.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization
            
        Returns:
            Dict: Average tenure metrics with weekly granularity
        """
        try:
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided")
                return {
                    'success': False,
                    'error': 'Company ID is required'
                }

            # Get all employees with their start dates, excluding Business Owners
            employees = (
                self.db_session.query(
                    Employees.employee_id,
                    Employees.start_date,
                    Employees.end_date
                )
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.start_date.isnot(None),  # Ensure start_date exists
                    Employees.role != 'Business Owner'  # Exclude Business Owners
                )
                .all()
            )

            if not employees:
                return {
                    'success': True,
                    'data': []
                }

            # Calculate metrics for each week in the last year
            today = date.today()
            weekly_metrics = []

            for week_offset in range(52):  # Last 52 weeks
                analysis_date = today - relativedelta(weeks=week_offset)
                metrics = self._calculate_average_tenure_for_date(employees, analysis_date)
                weekly_metrics.append({
                    'date': analysis_date.strftime('%Y-%m-%d'),
                    'total_employees': metrics['total_employees'],
                    'average_tenure_months': metrics['average_tenure_months'],
                    'total_tenure_months': metrics['total_tenure_months']
                })

            return {
                'success': True,
                'data': sorted(weekly_metrics, key=lambda x: x['date'])
            }

        except Exception as e:
            logging.error(f"Error calculating average tenure metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_average_tenure_for_date(self, employees: List, analysis_date: date) -> Dict:
        """
        Calculate average tenure metrics for active employees at a specific date.
        
        Args:
            employees: List of employee records
            analysis_date: Date to calculate metrics for
            
        Returns:
            Dict: Metrics including total employees and average tenure in months
        """
        total_employees = 0
        total_tenure_months = 0

        for emp in employees:
            # Check if employee was active on analysis date
            if emp.start_date <= analysis_date and (
                emp.end_date is None or emp.end_date >= analysis_date
            ):
                total_employees += 1
                
                # Calculate tenure at analysis date
                tenure_months = (
                    (analysis_date.year - emp.start_date.year) * 12 + 
                    (analysis_date.month - emp.start_date.month)
                )
                
                total_tenure_months += tenure_months

        # Calculate average tenure
        average_tenure_months = (
            round(total_tenure_months / total_employees, 2)
            if total_employees > 0
            else 0
        )

        return {
            'total_employees': total_employees,
            'average_tenure_months': average_tenure_months,
            'total_tenure_months': total_tenure_months
        }

    def get_all_metrics(self, company_id: Optional[int] = None) -> Dict:
        """
        Get all metrics in a single efficient call.
        Returns retention, turnover, and average tenure metrics.
        """
        target_company_id = company_id if company_id is not None else self.company_id
        
        if target_company_id is None:
            return {'success': False, 'error': 'Company ID is required'}

        # For all metrics at once (most efficient)
        manager = TenureAnalysisManager(company_id=target_company_id)

        # Or for individual metrics (still optimized due to caching)
        tenure_metrics = manager.calculate_average_tenure()
        turnover_metrics = manager.calculate_turnover_metrics()
        retention_metrics = manager.calculate_tenure_metrics()

        return {
            'success': True,
            'data': {
                'retention': [{
                    'date': m['date'],
                    'total_employees': m['total_employees'],
                    'retention_rate': m['retention_rate'],
                    'retained_count': m['retained_count']
                } for m in retention_metrics['data']],
                'turnover': [{
                    'date': m['date'],
                    'total_employees': m['total_employees'],
                    'employees_left': m['employees_left'],
                    'turnover_rate': m['turnover_rate'],
                    'turnover_rate_ma': m['turnover_rate_ma']
                } for m in turnover_metrics['data']],
                'tenure': [{
                    'date': m['date'],
                    'total_employees': m['total_employees'],
                    'average_tenure_months': m['average_tenure_months'],
                    'total_tenure_months': m['total_tenure_months']
                } for m in tenure_metrics['data']]
            }
        }

