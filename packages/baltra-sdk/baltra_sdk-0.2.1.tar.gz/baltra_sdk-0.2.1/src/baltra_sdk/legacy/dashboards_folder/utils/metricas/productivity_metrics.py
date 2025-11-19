from baltra_sdk.legacy.dashboards_folder.models import db, Rewards
from sqlalchemy import func, desc, and_, cast, Numeric
from typing import List, Dict, Optional
import logging
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class ProductivityMetricsManager:
    """
    Class for managing employee productivity metrics analysis.
    Calculates weekly attendance and punctuality rates based on Rewards data.
    """
    
    def __init__(self, company_id: int = None):
        """
        Initialize the ProductivityMetricsManager.
        
        Args:
            company_id (int, optional): The ID of the company to analyze
        """
        self.company_id = company_id
        self.db_session = db.session

    def _calculate_metric_for_week(self, company_id: int, start_date: date, end_date: date, metric_type: str) -> Dict:
        """
        Calculate metrics for a specific date range.
        
        Args:
            company_id: Company ID to filter records
            start_date: Start date of the period (inclusive)
            end_date: End date of the period (inclusive)
            metric_type: Type of metric ('attendance' or 'punctuality')
            
        Returns:
            Dict: Metrics including total records, present/on-time count, and rate
        """
        try:
            # Query to get total valid records and present/on-time count
            result = (
                self.db_session.query(
                    func.count().label('total'),
                    func.sum(
                        cast(Rewards.score, Numeric)
                    ).label('present_count')
                )
                .filter(
                    Rewards.company_id == company_id,
                    Rewards.date >= start_date,
                    Rewards.date <= end_date,
                    Rewards.metric == metric_type,
                    Rewards.score != 'n/a'  # Filter out n/a scores
                )
                .first()
            )

            total = result.total if result.total else 0
            present_count = float(result.present_count) if result.present_count else 0

            # Calculate rate
            rate = round((present_count / total) * 100, 2) if total > 0 else 0

            return {
                'total': total,
                'present': int(present_count),
                'rate': rate
            }

        except Exception as e:
            logging.error(f"Error calculating {metric_type} metrics for date range {start_date} to {end_date}: {str(e)}")
            return {
                'total': 0,
                'present': 0,
                'rate': 0
            }

    def calculate_weekly_metrics(self, company_id: Optional[int] = None, num_weeks: int = 52) -> Dict:
        """
        Calculate weekly attendance and punctuality percentages.
        Filters out 'n/a' scores and computes percentages based on valid records.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization
            num_weeks (int, optional): Number of weeks to calculate metrics for. Defaults to 52.
                                     Use 1 for current week only.
            
        Returns:
            Dict: Weekly metrics for attendance and punctuality
        """
        try:
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided")
                return {
                    'success': False,
                    'error': 'Company ID is required'
                }

            # Get the oldest attendance record date
            oldest_record = (
                self.db_session.query(Rewards.date)
                .filter(
                    Rewards.company_id == target_company_id,
                    Rewards.metric == 'attendance'
                )
                .order_by(Rewards.date.asc())
                .first()
            )

            most_recent_record = (
                self.db_session.query(Rewards.date)
                .filter(
                    Rewards.company_id == target_company_id,
                    Rewards.metric == 'attendance'
                )
                .order_by(Rewards.date.desc())
                .first()
            )

            if not oldest_record:
                logging.warning(f"No attendance records found for company {target_company_id}")
                return {
                    'success': True,
                    'data': []
                }

            oldest_date = oldest_record.date
            most_recent_date = most_recent_record.date

            # Calculate total weeks between oldest record and today
            total_weeks = ((most_recent_date - oldest_date).days // 7) + 1
            
            # Use the smaller of 52 weeks or total available weeks
            weeks_to_fetch = min(num_weeks, total_weeks)
            
            weekly_metrics = []

            for week_offset in range(weeks_to_fetch):
                analysis_date = most_recent_date - relativedelta(weeks=week_offset)
                monday_date = analysis_date - relativedelta(days=analysis_date.weekday())
                sunday_date = monday_date + relativedelta(days=6)

                # Calculate attendance metrics for the week
                attendance_metrics = self._calculate_metric_for_week(
                    target_company_id,
                    monday_date,
                    sunday_date,
                    'attendance'
                )

                # Calculate punctuality metrics for the week
                punctuality_metrics = self._calculate_metric_for_week(
                    target_company_id,
                    monday_date,
                    sunday_date,
                    'punctuality'
                )

                weekly_metrics.append({
                    'date': monday_date.strftime('%Y-%m-%d'),
                    'week': monday_date.strftime('%Y-%m-%d'),
                    'year': monday_date.year,
                    'start_date': monday_date.strftime('%Y-%m-%d'),
                    'end_date': sunday_date.strftime('%Y-%m-%d'),
                    'attendance_rate': attendance_metrics['rate'],
                    'attendance_total': attendance_metrics['total'],
                    'attendance_present': attendance_metrics['present'],
                    'punctuality_rate': punctuality_metrics['rate'],
                    'punctuality_total': punctuality_metrics['total'],
                    'punctuality_on_time': punctuality_metrics['present']
                })

            logging.info(f"Weekly metrics: {weekly_metrics}")

            return {
                'success': True,
                'data': sorted(weekly_metrics, key=lambda x: x['date'])
            }

        except Exception as e:
            logging.error(f"Error calculating productivity metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

