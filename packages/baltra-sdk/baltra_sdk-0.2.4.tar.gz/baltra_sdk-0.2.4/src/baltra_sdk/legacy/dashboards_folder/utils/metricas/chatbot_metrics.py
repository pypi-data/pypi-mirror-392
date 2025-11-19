import logging
from sqlalchemy import func, cast, Float, distinct, case, text, and_
from baltra_sdk.legacy.dashboards_folder.models import db, Employees, Messages, Sentiment, Companies
from datetime import datetime, timedelta, date
from collections import defaultdict
from typing import Optional

class ChatbotMetricsManager:
    """
    Manages the calculation of chatbot engagement, survey response rates,
    and sentiment analysis metrics with weekly granularity for the past 6 months.
    """

    def __init__(self, company_id: int):
        """
        Initialize the manager.

        Args:
            company_id (int): The ID of the company to analyze.
        """
        if not company_id:
            raise ValueError("Company ID is required")
        self.company_id = company_id
        self.db_session = db.session
        self.six_months_ago = date.today() - timedelta(weeks=26)

    def _get_weekly_active_employees(self) -> dict[date, int]:
        """
        Calculates the number of active employees for each week starting from 6 months ago.
        An employee is active in a week if they were active during that week (Mon-Sun).
        Excludes 'Business Owner' role.

        Returns:
            dict[date, int]: Dictionary mapping week start date (Sunday based on date_trunc) to active employee count.
        """
        try:
            # Calculate the actual start date (Sunday of the week containing six_months_ago) using Python
            six_months_ago_date = self.six_months_ago
            days_since_sunday = (six_months_ago_date.weekday() + 1) % 7 # Assuming Monday is 0, Sunday is 6
            min_week_start_date = six_months_ago_date - timedelta(days=days_since_sunday)

            # Generate all relevant week start dates (Sundays based on date_trunc default)
            weeks = {}
            current_week_start = min_week_start_date
            
            latest_sentiment_date = self.db_session.query(
                func.max(Sentiment.date)
            ).filter(
                Sentiment.company_id == self.company_id
            ).scalar()

            if not latest_sentiment_date:
                # No sentiment records found, fallback to today or return empty dict early
                logging.warning(f"No sentiment data found for company {self.company_id}, using today's date for range")
                latest_sentiment_date = date.today()
            
            while current_week_start <= latest_sentiment_date:
                weeks[current_week_start] = 0
                current_week_start += timedelta(days=7)

            # Query employees potentially active during the period
            active_employees_query = self.db_session.query(
                Employees.employee_id,
                Employees.start_date,
                Employees.end_date
            ).filter(
                Employees.company_id == self.company_id,
                Employees.role != 'Business Owner',
                Employees.start_date.isnot(None),
                Employees.start_date <= latest_sentiment_date, # Started before or on latest_sentiment_date
                (Employees.end_date.is_(None) | (Employees.end_date >= min_week_start_date)) # Active at some point in the window
            ).all()

            # Efficiently count active employees for each week
            for week_start in weeks.keys():
                week_end = week_start + timedelta(days=6) # Sunday to Saturday
                count = 0
                for emp in active_employees_query:
                    # Check for overlap: employee interval overlaps with week interval
                    emp_start = emp.start_date
                    emp_end = emp.end_date if emp.end_date else date.max # Use max date for open-ended employment

                    # Condition: (EmpStart <= WeekEnd) and (EmpEnd >= WeekStart)
                    if emp_start <= week_end and emp_end >= week_start:
                         count += 1
                weeks[week_start] = count


            logging.info(f"Calculated active employees for {len(weeks)} weeks for company {self.company_id}.")
            # Filter out weeks with zero employees if necessary, though maybe keep for context
            # return {wk: count for wk, count in weeks.items() if count > 0}
            return weeks

        except Exception as e:
            logging.error(f"Error calculating weekly active employees for company {self.company_id}: {e}", exc_info=True)
            return {}


    def _get_weekly_engagement(self, weekly_active_employees: dict[date, int]) -> dict[date, float]:
        """
        Calculates the percentage of active employees who sent a message each week.

        Args:
            weekly_active_employees (dict[date, int]): Pre-calculated active employees per week.

        Returns:
            dict[date, float]: Dictionary mapping week start date (Sunday) to engagement rate (0-100).
        """
        try:
            # Explicitly set to Sunday-based weeks to match _get_weekly_active_employees
            week_start_expr = (
                (func.date_trunc('week', Messages.time_stamp + text("INTERVAL '1 day'"))
                - text("INTERVAL '1 day'")).cast(db.Date)
            )
            
            weekly_engaged_counts = self.db_session.query(
                week_start_expr.label('week_start'),
                func.count(distinct(Messages.employee_id)).label('engaged_count')
            ).filter(
                Messages.company_id == self.company_id,
                Messages.sent_by == 'user',
                Messages.time_stamp >= self.six_months_ago
            ).group_by('week_start').all()
            logging.info(f"Weekly engaged counts: {weekly_engaged_counts}")
            engaged_counts_map = {row.week_start: row.engaged_count for row in weekly_engaged_counts}

            engagement_rates = {}
            for week_start, total_active in weekly_active_employees.items():
                 if total_active > 0:
                    engaged_count = engaged_counts_map.get(week_start, 0)
                    rate = round((engaged_count / total_active) * 100, 2)
                 else:
                    rate = 0.0
                 engagement_rates[week_start] = rate

            logging.info(f"Calculated weekly engagement rates for company {self.company_id}.")
            logging.info(f"Engagement rates: {engagement_rates}")
            return engagement_rates

        except Exception as e:
            logging.error(f"Error calculating weekly engagement for company {self.company_id}: {e}", exc_info=True)
            return {}

    def _get_weekly_survey_response_rate(self, weekly_active_employees: dict[date, int]) -> dict[date, float]:
        """
        Calculates the percentage of active employees who responded to the sentiment survey each week.

        Args:
            weekly_active_employees (dict[date, int]): Pre-calculated active employees per week.

        Returns:
            dict[date, float]: Dictionary mapping week start date (Sunday) to survey response rate (0-100).
        """
        try:
            # Explicitly set to Sunday-based weeks to match _get_weekly_active_employees
            week_start_expr = (
                (func.date_trunc('week', Sentiment.date + text("INTERVAL '1 day'"))
                - text("INTERVAL '1 day'")).cast(db.Date)
            )

            weekly_responded_counts = self.db_session.query(
                week_start_expr.label('week_start'),
                func.count(distinct(Sentiment.employee_id)).label('responded_count')
            ).filter(
                Sentiment.company_id == self.company_id,
                Sentiment.score.isnot(None),
                Sentiment.score != '', # Handle empty strings if score is text
                Sentiment.date >= self.six_months_ago
            ).group_by('week_start').all()
            
            logging.info(f"Weekly responded counts: {weekly_responded_counts}")
            responded_counts_map = {row.week_start: row.responded_count for row in weekly_responded_counts}

            response_rates = {}
            for week_start, total_active in weekly_active_employees.items():
                 if total_active > 0:
                    responded_count = responded_counts_map.get(week_start, 0)
                    rate = round((responded_count / total_active) * 100, 2)
                 else:
                    rate = 0.0
                 response_rates[week_start] = rate

            logging.info(f"Calculated weekly survey response rates for company {self.company_id}.")
            logging.info(f"Response rates: {response_rates}")
            return response_rates

        except Exception as e:
            logging.error(f"Error calculating weekly survey response rate for company {self.company_id}: {e}", exc_info=True)
            return {}


    def _get_weekly_sentiment_by_category(self) -> dict[date, dict[str, Optional[float]]]:
        """
        Calculates the average sentiment score for each category ('communication with manager',
        'motivation', 'work environment') per week.

        Returns:
            dict[date, dict[str, float | None]]: Dictionary mapping week start date (Sunday)
                                                  to a dict of category averages.
        """
        try:
            week_start_expr = func.date_trunc('week', Sentiment.date - text("INTERVAL '1 day'")).cast(db.Date) + text("INTERVAL '1 day'")
            score_numeric = cast(func.nullif(Sentiment.score, ''), Float) # Handle empty strings

            results = self.db_session.query(
                week_start_expr.label('week_start'),
                Sentiment.metric,
                func.avg(score_numeric).label('average_score')
            ).filter(
                Sentiment.company_id == self.company_id,
                Sentiment.metric.in_(['communication with manager', 'motivation', 'work environment']),
                Sentiment.date >= self.six_months_ago,
                # Add robust numeric check if scores can be non-numeric text
                # e.g., using try_cast or regex depending on DB
                # Sentiment.score.op('~')('^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')
            ).group_by('week_start', Sentiment.metric).order_by('week_start').all()

            sentiment_by_week = defaultdict(lambda: {
                'comunicacion_avg': None,
                'motivacion_avg': None,
                'ambiente_laboral_avg': None
            })

            metric_map = {
                'communication with manager': 'comunicacion_avg',
                'motivation': 'motivacion_avg',
                'work environment': 'ambiente_laboral_avg'
            }

            for row in results:
                if row.week_start and row.metric in metric_map and row.average_score is not None:
                     key = metric_map[row.metric]
                     sentiment_by_week[row.week_start][key] = round(row.average_score, 2)

            logging.info(f"Calculated weekly sentiment by category for company {self.company_id}.")
            return dict(sentiment_by_week)

        except Exception as e:
            logging.error(f"Error calculating weekly sentiment by category for company {self.company_id}: {e}", exc_info=True)
            return {}

    def _get_weekly_sentiment_questions(self) -> dict[date, list[dict]]:
        """
        Gets the unique questions asked in sentiment surveys for each week, including their weighted average scores and metrics.

        Returns:
            dict[date, list[dict]]: Dictionary mapping week start date (Sunday) to list of question objects with weighted scores and metrics.
        """
        try:
            # Explicitly set to Sunday-based weeks to match other methods
            week_start_expr = (
                (func.date_trunc('week', Sentiment.date + text("INTERVAL '1 day'"))
                - text("INTERVAL '1 day'")).cast(db.Date)
            )

            # Calculate weighted average: (sum of scores) / (total responses)
            score_numeric = cast(func.nullif(Sentiment.score, ''), Float)
            
            results = self.db_session.query(
                week_start_expr.label('week_start'),
                Sentiment.question,
                Sentiment.metric,
                func.sum(score_numeric).label('total_score'),
                func.count(Sentiment.sentiment_id).label('response_count'),
                (func.sum(score_numeric) / func.count(Sentiment.sentiment_id)).label('weighted_average_score')
            ).filter(
                Sentiment.company_id == self.company_id,
                Sentiment.question.isnot(None),
                Sentiment.question != '',
                Sentiment.score.isnot(None),
                Sentiment.score != '',
                Sentiment.date >= self.six_months_ago
            ).group_by('week_start', Sentiment.question, Sentiment.metric).order_by('week_start', Sentiment.question).all()

            questions_by_week = {}
            for row in results:
                if row.week_start and row.question and row.weighted_average_score is not None:
                    week_start = row.week_start
                    
                    # Initialize the week if it doesn't exist
                    if week_start not in questions_by_week:
                        questions_by_week[week_start] = []
                    
                    # Create question object with weighted average data
                    question_data = {
                        'question': row.question,
                        'metric': row.metric,
                        'weighted_average_score': round(row.weighted_average_score, 2),
                        'total_score': round(row.total_score, 2),
                        'response_count': row.response_count
                    }
                    
                    # Add to the week's list
                    questions_by_week[week_start].append(question_data)

            logging.info(f"Calculated weekly sentiment questions with weighted scores for company {self.company_id}.")
            return questions_by_week

        except Exception as e:
            logging.error(f"Error calculating weekly sentiment questions for company {self.company_id}: {e}", exc_info=True)
            return {}

    def _get_latest_overall_sentiment(self) -> Optional[float]:
        """
        Calculates the overall average sentiment score for the most recent week with data.

        Returns:
            float | None: The overall average sentiment score, or None if no data.
        """
        try:
            latest_week_start = self.db_session.query(
                func.max(func.date_trunc('week', Sentiment.date - text("INTERVAL '1 day'")).cast(db.Date) + text("INTERVAL '1 day'"))
            ).filter(
                Sentiment.company_id == self.company_id,
                Sentiment.metric.in_(['communication with manager', 'motivation', 'work environment']),
                Sentiment.date >= self.six_months_ago,
                Sentiment.score.isnot(None),
                Sentiment.score != ''
                # Add numeric filter if needed
            ).scalar()

            if not latest_week_start:
                logging.warning(f"No recent sentiment data found for company {self.company_id}.")
                return None

            score_numeric = cast(func.nullif(Sentiment.score, ''), Float)
            average_score = self.db_session.query(func.avg(score_numeric)).filter(
                Sentiment.company_id == self.company_id,
                func.date_trunc('week', Sentiment.date - text("INTERVAL '1 day'")).cast(db.Date) + text("INTERVAL '1 day'") == latest_week_start,
                Sentiment.metric.in_(['communication with manager', 'motivation', 'work environment'])
                # Add numeric filter if needed
            ).scalar()

            latest_score = round(average_score, 2) if average_score is not None else None
            logging.info(f"Calculated latest overall sentiment for company {self.company_id}: {latest_score}")
            return latest_score

        except Exception as e:
            logging.error(f"Error calculating latest overall sentiment for company {self.company_id}: {e}", exc_info=True)
            return None


    def get_all_chatbot_metrics(self) -> dict:
        """
        Calculates and aggregates all chatbot and sentiment metrics.

        Returns:
            dict: A dictionary containing structured metrics data.
                  Includes keys: 'success', 'data' (with sub-keys for each metric type),
                  or 'success', 'error' on failure.
        """
        try:
            logging.info(f"Starting all chatbot metrics calculation for company {self.company_id}")

            weekly_active_employees = self._get_weekly_active_employees()
            weekly_sentiment = self._get_weekly_sentiment_by_category()
            latest_sentiment = self._get_latest_overall_sentiment()
            weekly_sentiment_questions = self._get_weekly_sentiment_questions()

            if not weekly_active_employees:
                 logging.warning(f"Could not determine weekly active employees for company {self.company_id}. Returning empty rate data.")
                 weekly_engagement_response = []
            else:
                weekly_engagement = self._get_weekly_engagement(weekly_active_employees)
                weekly_response_rate = self._get_weekly_survey_response_rate(weekly_active_employees)

                # Combine rates, ensuring all weeks from active_employees are present
                weekly_engagement_response = []
                all_weeks = sorted(weekly_active_employees.keys())
                for week_start in all_weeks:
                    weekly_engagement_response.append({
                        'date': week_start.strftime('%Y-%m-%d'),
                        'engagement_rate': weekly_engagement.get(week_start, 0.0),
                        'response_rate': weekly_response_rate.get(week_start, 0.0)
                    })

            # Format sentiment data
            formatted_sentiment = [
                 {'date': dt.strftime('%Y-%m-%d'), **scores}
                 for dt, scores in sorted(weekly_sentiment.items())
            ]

            # Format sentiment questions data
            formatted_sentiment_questions = [
                {
                    'date': dt.strftime('%Y-%m-%d'),
                    'questions': questions
                }
                for dt, questions in sorted(weekly_sentiment_questions.items(), reverse=True)
            ]

            logging.info(f"Successfully calculated all chatbot metrics for company {self.company_id}")
            return {
                'success': True,
                'data': {
                    'weekly_engagement_response': weekly_engagement_response,
                    'weekly_sentiment_by_category': formatted_sentiment,
                    'latest_overall_sentiment': latest_sentiment,
                    'weekly_sentiment_questions': formatted_sentiment_questions
                }
            }

        except Exception as e:
            logging.error(f"Failed to get all chatbot metrics for company {self.company_id}: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'An error occurred while calculating chatbot metrics: {str(e)}'
            }
