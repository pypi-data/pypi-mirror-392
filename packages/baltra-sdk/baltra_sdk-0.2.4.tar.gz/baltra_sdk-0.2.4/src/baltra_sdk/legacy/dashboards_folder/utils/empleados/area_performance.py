# area_performance.py
from baltra_sdk.legacy.dashboards_folder.models import db, Points, Sentiment, Rewards, Employees
from sqlalchemy import func, desc, distinct, and_, case
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

class AreaPerformanceManager:
    """
    Class for managing area performance metrics including points, sentiment, 
    performance, and employee counts grouped by sub_area or area.
    """
    
    def __init__(self, company_id: int = None):
        """
        Initialize the AreaPerformanceManager.
        
        Args:
            company_id (int, optional): The ID of the company to analyze
        """
        self.company_id = company_id
        self.db_session = db.session

    def get_area_performance_table(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Get performance metrics grouped by sub_area, or area if company_id is 9.
        
        Args:
            company_id (int, optional): Override the company_id set during initialization
            
        Returns:
            List[Dict]: List of area performance data with rankings
        """
        try:
            target_company_id = company_id if company_id is not None else self.company_id
            
            if target_company_id is None:
                logging.error("No company ID provided")
                return []

            latest_date = datetime.now().date()
            one_month_ago = latest_date - timedelta(days=30)

            # Determine grouping column
            grouping_col = Employees.area if target_company_id == 9 else Employees.sub_area

            # Sum points by grouping column
            points_subq = (
                self.db_session.query(
                    grouping_col.label('group_name'),
                    (func.coalesce(func.sum(Points.points), 0) / func.count(distinct(Employees.employee_id))).label('avg_points')
                )
                .outerjoin(Points, 
                    and_(
                        Points.employee_id == Employees.employee_id,
                        Points.date >= one_month_ago,
                        Points.date <= latest_date,
                        Points.transaction == 'points earned'
                    )
                )
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.active == True,
                    Employees.left_company == False
                )
                .group_by(grouping_col)
                .subquery()
            )

            # Average sentiment
            sentiment_subq = (
                self.db_session.query(
                    grouping_col.label('group_name'),
                    func.avg(func.cast(Sentiment.score, db.Float)).label('avg_sentiment')
                )
                .join(Sentiment, Sentiment.employee_id == Employees.employee_id)
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.active == True,
                    Sentiment.date >= one_month_ago,
                    Sentiment.date <= latest_date
                )
                .group_by(grouping_col)
                .subquery()
            )

            # Survey response rate
            survey_response_subq = (
                self.db_session.query(
                    grouping_col.label('group_name'),
                    (func.sum(case((Sentiment.score.isnot(None), 1), else_=0)) * 100.0 / 
                     func.count(Sentiment.sentiment_id)).label('response_rate')
                )
                .join(Sentiment, 
                    and_(
                        Sentiment.employee_id == Employees.employee_id,
                        Sentiment.date >= one_month_ago,
                        Sentiment.date <= latest_date
                    )
                )
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.active == True,
                    Employees.left_company == False,
                    Employees.role != 'Business Owner',
                    Employees.start_date <= latest_date - timedelta(days=7)
                )
                .group_by(grouping_col)
                .subquery()
            )

            # Employee count
            employee_count_subq = (
                self.db_session.query(
                    grouping_col.label('group_name'),
                    func.count(Employees.employee_id).label('employee_count')
                )
                .filter(
                    Employees.company_id == target_company_id,
                    Employees.active == True,
                    Employees.left_company == False
                )
                .group_by(grouping_col)
                .subquery()
            )

            # Combine all metrics
            results = (
                self.db_session.query(
                    employee_count_subq.c.group_name,
                    points_subq.c.avg_points,
                    sentiment_subq.c.avg_sentiment,
                    survey_response_subq.c.response_rate,
                    employee_count_subq.c.employee_count
                )
                .select_from(employee_count_subq)
                .outerjoin(points_subq, points_subq.c.group_name == employee_count_subq.c.group_name)
                .outerjoin(sentiment_subq, sentiment_subq.c.group_name == employee_count_subq.c.group_name)
                .outerjoin(survey_response_subq, survey_response_subq.c.group_name == employee_count_subq.c.group_name)
                .order_by(desc(points_subq.c.avg_points))
                .all()
            )

            # Format results with ranking
            formatted_results = []
            for rank, row in enumerate(results, 1):
                formatted_results.append({
                    'rank': rank,
                    'area': row.group_name or 'Sin área1',
                    'puntos_promedio': round(float(row.avg_points or 0), 2),
                    'satisfaccion': round(float(row.avg_sentiment or 0), 2),
                    'tasa_respuesta': round(float(row.response_rate or 0), 2),
                    'empleados': row.employee_count,
                    'periodo': f"{one_month_ago.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}"
                })

            return formatted_results

        except Exception as e:
            logging.error(f"Error getting area performance table: {str(e)}")
            return []
