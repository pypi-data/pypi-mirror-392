from flask import current_app
import logging
from datetime import datetime, timedelta, timezone
from baltra_sdk.legacy.dashboards_folder.models import (
    db, Employees, 
    Points, Sentiment,
    RewardRules, GroupRewards,
    Rewards
)

"""
Main function to run the rewards processor
This script processes group and individual rewards based on a given company_id, week, and interval.
It handles two main classes: GroupRewardProcessor and IndividualRewardProcessor.
- GroupRewardProcessor processes group-level rewards.
- IndividualRewardProcessor processes individual rewards such as encuesta and attendance/punctuality rewards.

This is triggered from a flask command 
"""

#Class for processing group reward points for employees based on performance metrics.
class GroupRewardProcessor:
    """
    This class is designed to calculate and store reward points for employees in a given company 
    based on group performance metrics such as productivity, punctuality, and attendance. The reward 
    points are calculated using pre-defined rules that vary by time interval (weekly, biweekly, monthly) 
    and are assigned to employees in different areas.

    Attributes:
        company_id (int): The ID of the company for which group rewards are being processed.
        interval (str): The time interval (e.g., "weekly", "biweekly", "monthly") to filter reward rules.
        multiplier (float): A multiplier to apply to the final points value (default: 1.0).
    """
    def __init__(self, company_id: int, interval: str, multiplier: float = 1.0):
        self.company_id = company_id
        self.interval = interval
        self.multiplier = multiplier
        logging.info(f"GroupRewardProcessor initialized for company_id: {self.company_id} with multiplier: {self.multiplier}")

    def fetch_reward_rules(self):
        """Fetch all reward rules for the given company, filtered by interval."""
        logging.debug(f"Fetching reward rules for company_id: {self.company_id}")
        
        # Base query
        query = db.session.query(RewardRules).filter_by(company_id=self.company_id, rule_type='group')
        
        # Add interval filter based on the given interval
        if self.interval == "weekly":
            query = query.filter(RewardRules.interval == "weekly")
        elif self.interval == "biweekly":
            query = query.filter(RewardRules.interval.in_(["weekly", "biweekly"]))
        elif self.interval == "monthly":
            query = query.filter(RewardRules.interval.in_(["weekly", "biweekly", "monthly"]))
        
        reward_rules = query.all()
        logging.debug(f"Found {len(reward_rules)} reward rules for company_id: {self.company_id} with interval: {self.interval}")
        return reward_rules

    def fetch_group_rewards(self, area: str, metric: str, week: int):
        """Retrieve group performance metrics for calculations."""
        logging.info(f"Fetching group rewards for area: {area}, metric: {metric}, week: {week}")
        group_reward = db.session.query(GroupRewards).filter_by(
            company_id=self.company_id, area=area, metric=metric, week=week
        ).first()
        if group_reward:
            logging.info(f"Found group reward for area: {area}, metric: {metric}, week: {week} with score: {group_reward.score}")
        else:
            logging.info(f"No group reward found for area: {area}, metric: {metric}, week: {week}")
        return group_reward

    def compute_points(self, metric_value, points_json):
        """Apply step-based logic to determine awarded points."""
        steps = points_json.get("steps", [])
        for step in steps:
            min_val = step.get("min")
            max_val = step.get("max")
            if max_val == 100:
                max_val = max_val*1.0000001
            points = step.get("points")
            
            if min_val <= metric_value < max_val:
                logging.debug(f"Metric value {metric_value} matched step: {min_val} <= value < {max_val}, awarding {points} points")
                return points
        logging.warning(f"No matching step found for metric value {metric_value}, returning 0 points")
        return 0  # Default to zero points if no step matches

    def calculate_group_rewards(self, week: int):
        """Calculate and store rewards based on group performance."""
        logging.info(f"Calculating group rewards for week: {week}")
        # Fetch all group reward rules
        rules = self.fetch_reward_rules()
        results = []
        
        for rule in rules:
            if rule.rule_type != "group":  # Only process group rules
                logging.info(f"Skipping rule {rule.metric_name} as it's not a 'group' rule")
                continue

            metric_name = rule.metric_name
            points_json = rule.points_json
            # Fetch the group rewards data for the given week
            group_reward = self.fetch_group_rewards(rule.area, metric_name, week)
            if not group_reward:
                logging.warning(f"No group reward data found for area: {rule.area}, metric: {metric_name}, week: {week}")
                continue  # No data available for this metric
            
            metric_value = 100*(group_reward.score / group_reward.objective)

            points = self.compute_points(metric_value, points_json)

            results.append({"area": rule.area, "metric": metric_name, "points": points, "week": week})

        return results

    def get_employee_level_saks_carnes(self, employee_id):
        """Calculate employee level based on months since start date for SAKS (company_id=6)"""
        try:
            employee = db.session.query(Employees.start_date).filter(
                Employees.employee_id == employee_id
            ).first()
            
            if not employee or not employee.start_date:
                logging.warning(f"No start date found for employee {employee_id}")
                return 1
            
            months_employed = (datetime.now().date() - employee.start_date).days / 30
            
            if months_employed < 3:
                return 1
            elif months_employed < 10:
                return 2
            else:
                return 3
            
        except Exception as e:
            logging.error(f"Error calculating level for employee {employee_id}: {e}")
            return 1

    def process_rewards(self, week: int):
        """Main function to process and store reward points."""
        logging.info(f"Processing rewards for week: {week}")
        results = self.calculate_group_rewards(week)
        
        total_employees = 0
        total_inserted = 0
        total_duplicates = 0
        
        # Insert points into Points table for each employee in the respective areas
        for result in results:
            area = result["area"]
            metric = result["metric"]
            points_value = result["points"]
            
            # Find all active employees in the specified area and company
            employees = db.session.query(Employees).filter_by(
                company_id=self.company_id, 
                sub_area=area,
                active=True
            ).all()
            
            logging.info(f"Found {len(employees)} active employees in area '{area}' for company_id: {self.company_id}")
            total_employees += len(employees)
            
            inserted_count = 0
            duplicate_count = 0
            
            # Insert points for each employee
            for employee in employees:
                # Check if a record with the same key attributes already exists
                existing_record = db.session.query(Points).filter_by(
                    employee_id=employee.employee_id,
                    company_id=self.company_id,
                    week=week,
                    metric=metric,
                    transaction="points earned"
                ).first()
                
                if existing_record:
                    logging.info(f"Duplicate record detected for employee_id={employee.employee_id}, week={week}, metric={metric}. Skipping.")
                    duplicate_count += 1
                    continue
                
                # Determine employee level
                if self.company_id == 6 or self.company_id == 7:
                    employee_level = self.get_employee_level_saks_carnes(employee.employee_id)
                else:
                    employee_level = 1
                
                # Calculate sub_points as sub_points * multiplier
                sub_points = points_value * self.multiplier
                final_points = sub_points * employee_level 
                
                new_point = Points(
                    employee_id=employee.employee_id,
                    company_id=self.company_id,
                    week=week,
                    date=datetime.now().date(),
                    area=area,
                    metric=metric,
                    transaction="points earned",
                    points=final_points,  # Final points (sub_points * levels * multiplier)
                    levels=employee_level,
                    sub_points=sub_points  # Original points value
                )
                db.session.add(new_point)
                inserted_count += 1
            
            try:
                db.session.commit()
                logging.info(f"Successfully added {inserted_count} entries to Points table for area '{area}', metric '{metric}'")
                total_inserted += inserted_count
                total_duplicates += duplicate_count
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error adding points to Points table: {str(e)}")
        
        logging.info(f"Total employees processed: {total_employees}")
        logging.info(f"Total records inserted: {total_inserted}")
        logging.info(f"Total duplicates skipped: {total_duplicates}")
        
        # Add counts to the results
        results_with_counts = {
            "results": results,
            "total_employees": total_employees,
            "inserted": total_inserted,
            "duplicates": total_duplicates
        }
        
        return results_with_counts

#Class responsible for calculating and processing reward points for employees in a company.
class IndividualRewardProcessor:
    """
    The processor calculates points based on different metrics like:
    - Encuesta (survey completion)
    - Punctuality and attendance

    It also interacts with the database to:
    - Fetch active employees
    - Retrieve reward rules based on the company and specified interval (weekly, biweekly, or monthly)
    - Calculate and store points for each employee based on the rules and their performance

    The class provides methods for:
    - Fetching active employees
    - Calculating points based on encuesta (survey)
    - Calculating points for punctuality and attendance
    - Handling employee level adjustments based on company-specific rules
    - Inserting calculated points into the Points table while avoiding duplicates
    - Managing intervals (weekly, biweekly, monthly) and verifying the correct number of records

    The process is batch-processed for performance optimization and handles any potential exceptions during point insertion.

    Attributes:
    - company_id (int): The unique identifier for the company whose employees' rewards are being processed.
    - interval (str): The interval type for reward calculations (weekly, biweekly, monthly) or 'custom'.
    - reward_rules (list): The list of reward rules retrieved for the company based on the specified interval.
    - multiplier (float): A multiplier to apply to encuesta points (default: 1.0).
    - start_date (datetime.date): Custom start date for punctuality/attendance calculations (only used when interval is 'custom').
    - end_date (datetime.date): Custom end date for punctuality/attendance calculations (only used when interval is 'custom').
    """

    def __init__(self, company_id: int, interval: str, multiplier: float = 1.0, start_date: datetime.date = None, end_date: datetime.date = None):
        self.company_id = company_id
        self.interval = interval
        self.multiplier = multiplier
        self.start_date = start_date
        self.end_date = end_date
        self.reward_rules = self.fetch_reward_rules() 
        logging.info(f"IndividualRewardProcessor initialized for company_id: {self.company_id} with multiplier: {self.multiplier}")
        if interval == 'custom':
            logging.info(f"Using custom date range: {self.start_date} to {self.end_date}")

    def fetch_active_employees(self):
        """Fetch all active employees for the given company."""
        logging.debug(f"Fetching active employees for company_id: {self.company_id}")
        active_employees = db.session.query(Employees).filter_by(company_id=self.company_id, active=True).all()
        logging.debug(f"Found {len(active_employees)} active employees for company_id: {self.company_id}")
        return active_employees
    
    def fetch_active_employees_sub_area(self, sub_area):
        """Fetch all active employees for the given company."""
        logging.debug(f"Fetching active employees for company_id: {self.company_id} in sub_area: {sub_area}")
        active_employees = db.session.query(Employees).filter_by(company_id=self.company_id, active=True, sub_area= sub_area).all()
        logging.debug(f"Found {len(active_employees)} active employees for company_id: {self.company_id} in sub_area: {sub_area}")

        return active_employees
    
    def fetch_reward_rules(self):
        """Fetch all reward rules for the given company, filtered by interval."""
        logging.debug(f"Fetching reward rules for company_id: {self.company_id}")
        
        # Base query
        query = db.session.query(RewardRules).filter_by(company_id=self.company_id, rule_type='individual')
        
        # Add interval filter based on the given interval
        if self.interval == "weekly":
            query = query.filter(RewardRules.interval == "weekly")
        elif self.interval == "biweekly":
            query = query.filter(RewardRules.interval.in_(["weekly", "biweekly"]))
        elif self.interval == "monthly":
            query = query.filter(RewardRules.interval.in_(["weekly", "biweekly", "monthly"]))
        
        reward_rules = query.all()
        logging.info(f"Found {len(reward_rules)} reward rules for company_id: {self.company_id} with interval: {self.interval}")
        return reward_rules

    def calculate_encuesta_points(self, employee_id):
        """Calculate points based on encuesta completion."""        
        # Get the previous week's date range
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday() + 7)
        end_of_week = start_of_week + timedelta(days=6)

        # Query survey data for the previous week
        encuesta_data = db.session.query(Sentiment).filter(
            Sentiment.employee_id == employee_id,
            Sentiment.date >= start_of_week,
            Sentiment.date <= end_of_week
        ).all()

        if not encuesta_data:
            logging.info(f'No sentiment data found for employee_id: {employee_id}')

        points = 0
        # Loop through the categories to check if the employee has a score for each one
        categories = ["work environment", "punctuality", "attendance"]
        category_scores = {category: None for category in categories}
        
        for data in encuesta_data:
            if data.metric in category_scores:
                category_scores[data.metric] = data.score

        # Check if at least one category has a score, and apply points
        if any(score is not None for score in category_scores.values()):
            for rule in self.reward_rules:  # Use the pre-fetched rules
                if rule.metric_name == "ENCUESTA":
                    steps = rule.points_json.get("steps", [])
                    for step in steps:
                        # Check if there's at least one score, which will always match the 1-1 step
                        if step.get("min") == 1 and step.get("max") == 1:
                            points = step.get("points")
                            break        
        return points
    
    def get_all_encuesta_points(self, week):
        logging.debug(f"Calculating all encuesta points")
        active_employees = self.fetch_active_employees()
        results = []

        for employee in active_employees:
            points = self.calculate_encuesta_points(employee.employee_id)  # Pass the employee_id from the active employees list
            results.append({"employee_id": employee.employee_id, "metric": 'encuesta', "points": points, "week": week})

        # Count 0 and non-zero points
        zero_points = sum(1 for result in results if result["points"] == 0)
        non_zero_points = len(results) - zero_points

        # Log the results
        logging.info(f"Zero points: {zero_points}, Non-zero points: {non_zero_points}")

        # Return results and counts
        return results
    
    def calculate_punctuality_attendance_points(self, week):
        """Calculates punctuality and attendance points for active employees, verifying the correct number of records based on the interval."""
        start_date, end_date = self.get_date_interval()
        if not start_date or not end_date:
            logging.error("Could not determine date range for punctuality/attendance calculations")
            return []

        logging.info(f"Calculating punctuality and attendance points from {start_date} to {end_date}")

        active_employees = self.fetch_active_employees()
        results = []

        # Get all punctuality & attendance rules for company
        punctuality_rules = [r for r in self.reward_rules if r.metric_name == "PUNTUALIDAD Y ASISTENCIA"]

        days_required = (end_date - start_date).days + 1

        for employee in active_employees:
            # Find applicable rules for this employee:
            applicable_rules = [r for r in punctuality_rules if r.area == "ALL" or r.area == employee.sub_area]

            if not applicable_rules:
                logging.warning(f"No punctuality/attendance reward rule found for employee {employee.employee_id} with sub_area '{employee.sub_area}'")
                continue

            # Pick specific rule if exists, else fallback to ALL
            rule = next((r for r in applicable_rules if r.area != "ALL"), None) or next((r for r in applicable_rules if r.area == "ALL"), None)

            if not rule:
                logging.warning(f"No punctuality/attendance rule found for employee {employee.employee_id}")
                continue

            steps = rule.points_json.get("steps", [])
            if not steps:
                logging.warning(f"No steps defined in punctuality/attendance rule for area '{rule.area}'")
                continue

            records = db.session.query(Rewards).filter(
                Rewards.employee_id == employee.employee_id,
                Rewards.date.between(start_date, end_date),
                Rewards.metric.in_(["attendance", "punctuality"])
            ).all()

            attendance_days = [r for r in records if r.metric == "attendance"]
            punctuality_days = [r for r in records if r.metric == "punctuality"]

            if len(attendance_days) != days_required or len(punctuality_days) != days_required:
                logging.warning(f"Insufficient records for employee_id {employee.employee_id} from {start_date} to {end_date}. Expected {days_required}, found {len(attendance_days)} attendance and {len(punctuality_days)} punctuality.")
                continue

            total_absences = sum(1 for r in attendance_days if r.score == '0')
            total_tardies = sum(1 for r in punctuality_days if r.score == '0')

            points = 0
            for step in steps:
                if total_absences <= step.get("max_absences", 0) and total_tardies <= step.get("max_tardies", 0):
                    points = step.get("points", 0)
                    break

            results.append({
                "employee_id": employee.employee_id,
                "metric": "puntualidad_asistencia",
                "points": points,
                "week": week
            })

        logging.info(f"Calculated punctuality and attendance points for {len(results)} employees.")
        return results

    
    def calculate_individual_rewards(self, week):
        """Calculates individual performance points for active employees
        Used for areas where performance is calculated individualy such as Brinco - Corte y Confección"""
        results = []
        for rule in self.reward_rules:
            if rule.metric_name in ["PUNTUALIDAD Y ASISTENCIA", "ENCUESTA"]:
                continue  # Skip already handled metrics
            if rule.area == "ALL":
                active_employees = self.fetch_active_employees()  # All active employees
            else:
                active_employees = self.fetch_active_employees_sub_area(rule.area)  # Filter by sub_area
            metric = rule.metric_name
            score = rule.individual_score
            objective = rule.individual_objective
            steps = rule.points_json.get("steps", [])

            for employee in active_employees:
                # Query the relevant metric data
                scores = db.session.query(Rewards).filter(
                    Rewards.employee_id == employee.employee_id,
                    Rewards.metric == score,
                    Rewards.week == week
                ).all()

                objectives = db.session.query(Rewards).filter(
                    Rewards.employee_id == employee.employee_id,
                    Rewards.metric == objective,
                    Rewards.week == week
                ).all()
                
                # Apply the reward rules logic
                points = 0
                if scores:
                    total_score = sum(float(r.score) for r in scores if r.score and r.score.replace('.', '', 1).isdigit())
                    total_objective = sum(float(r.score) for r in objectives if r.score and r.score.replace('.', '', 1).isdigit())
                    #That will  default total_objective to 1 in cases where: rule.individual_objective is None, or no Rewards rows matched the query.
                    total_objective = total_objective or 1

                    #If company works with percentages a cap and a normalizer of 100 is needed to ensure points are calculated correctly
                    #If company works with absolute numbers no cap is needed (set to a large number) and no normalizer needed (set to 1)
                    if self.company_id == 9:
                        cap = 10000000
                        normalizer = 1
                    else:
                        cap = 100
                        normalizer = 100
                    value = min(normalizer*(total_score / total_objective),cap) if total_objective else 0
                    logging.info(f'Total Score: {total_score} - Total Objective: {total_objective} - Value: {value}')
                    for step in steps:
                        if step.get("min") <= value <= step.get("max"):
                            points = step.get("points")
                            break
                
                results.append({"employee_id": employee.employee_id, "metric": metric, "points": points, "week": week})
        
        logging.info(f"Calculated individual rewards for {len(results)} employees.")
        return results
        

    def get_date_interval(self):
        """Returns the start and end date for the specified interval (weekly, biweekly, monthly, or custom)."""
        
        # If custom dates are provided, use them
        if self.interval == 'custom' and self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("Start date cannot be after end date")
            return self.start_date, self.end_date
        
        # Query the latest date for attendance or punctuality for the given company
        latest_record = db.session.query(Rewards.date).filter(
            Rewards.company_id == self.company_id,
            Rewards.metric.in_(["attendance", "punctuality"])
        ).order_by(Rewards.date.desc()).first()
        
        if not latest_record:
            logging.warning(f"No records found for company_id {self.company_id} in attendance or punctuality.")
            return None, None
        
        # Use the latest record date as the end_date
        end_date = latest_record.date

        if self.interval == "weekly":
            # Calculate the start date as 7 days prior to the end date
            start_date = end_date - timedelta(days=6)
        
        elif self.interval == "biweekly":
            # Determine if it's the first or second half of the month and set the start date accordingly
            if end_date.day <= 15:
                start_date = end_date.replace(day=1)  # Start of the month
            else:
                start_date = end_date.replace(day=16)  # Start of the second half of the month
        
        elif self.interval == "monthly":
            # Set the start date to the first day of the month
            start_date = end_date.replace(day=1)
        
        else:
            raise ValueError("Unsupported interval. Choose from 'weekly', 'biweekly', 'monthly', or 'custom'.")
        
        return start_date, end_date
    
    def get_employee_level_saks_carnes(self, employee_id):
        """Calculate employee level based on months since start date for SAKS (company_id=6)"""
        try:
            employee = db.session.query(Employees.start_date).filter(
                Employees.employee_id == employee_id
            ).first()
            
            if not employee or not employee.start_date:
                logging.warning(f"No start date found for employee {employee_id}")
                return 1
            
            months_employed = (datetime.now().date() - employee.start_date).days / 30
            
            if months_employed < 3:
                return 1
            elif months_employed < 10:
                return 2
            else:
                return 3
            
        except Exception as e:
            logging.error(f"Error calculating level for employee {employee_id}: {e}")
            return 1

    def _insert_points_to_database(self, results, week):
        """Helper method to insert points into the database."""
        if not results:
            logging.info("No results to insert into database")
            return 0, 0
        
        duplicate_count = 0
        inserted_count = 0
        
        # Batch process in smaller chunks to avoid potential issues with large datasets
        batch_size = 50
        for i in range(0, len(results), batch_size):
            batch = results[i:i+batch_size]
            batch_duplicates = 0
            batch_inserts = 0
            
            for result in batch:
                employee_id = result["employee_id"]
                points_value = result["points"]
                metric = result["metric"]
                
                # Get employee's sub_area from the employees table
                employee = db.session.query(Employees).filter_by(
                    employee_id=employee_id
                ).first()
                
                if not employee:
                    logging.warning(f"Employee with ID {employee_id} not found in database")
                    continue
                
                # Check if a record with the same key attributes already exists
                existing_record = db.session.query(Points).filter_by(
                    employee_id=employee_id,
                    company_id=self.company_id,
                    week=week,
                    metric=metric,
                    transaction="points earned"
                ).first()
                
                if existing_record:
                    logging.info(f"Duplicate record detected for employee_id={employee_id}, week={week}, metric={metric}. Skipping.")
                    duplicate_count += 1
                    batch_duplicates += 1
                    continue
                
                # Determine employee level
                if self.company_id == 6 or self.company_id == 7:
                    employee_level = self.get_employee_level_saks_carnes(employee_id)
                else:
                    employee_level = 1
                
                # Calculate final points as sub_points * levels * multiplier (only for encuesta)
                sub_points = points_value
                final_points = sub_points * employee_level
                if metric != 'puntualidad_asistencia':
                    sub_points = points_value * self.multiplier
                    final_points = sub_points * employee_level
                
                # Create new points entry
                new_point = Points(
                    employee_id=employee_id,
                    company_id=self.company_id,
                    week=week,
                    date=datetime.now().date(),
                    area=employee.sub_area if employee.sub_area else "",
                    metric=metric,
                    transaction="points earned",
                    points=final_points,  # Final points (sub_points * levels * multiplier for everything except puntualidad_asistencia)
                    levels=employee_level,
                    sub_points=sub_points  # Original points value (sub_points * multiplier for everything except puntualidad_asistencia)
                )
                
                try:
                    db.session.add(new_point)
                    batch_inserts += 1
                    inserted_count += 1
                except Exception as e:
                    logging.error(f"Error preparing points for employee {employee_id}: {str(e)}")
            
            if batch_inserts > 0:
                try:
                    db.session.commit()
                    logging.debug(f"Successfully committed {batch_inserts} points entries to Points table")
                except Exception as e:
                    db.session.rollback()
                    logging.error(f"Error committing points to Points table: {str(e)}")
                    inserted_count -= batch_inserts
        
        if duplicate_count > 0:
            logging.warning(f"Skipped {duplicate_count} duplicate records that already existed in the database")
        
        logging.info(f"Total records processed: {len(results)}, Inserted: {inserted_count}, Duplicates skipped: {duplicate_count}")
        
        return inserted_count, duplicate_count

    def process_rewards(self, week):
        """Main function to process and store reward points."""
        logging.info(f"Processing rewards for week: {week}")
        
        # Get encuesta points results
        encuesta_results = self.get_all_encuesta_points(week)
        logging.info(f"Retrieved {len(encuesta_results)} encuesta results for week {week}")
        
        # Get punctuality and attendance points
        attendance_results = self.calculate_punctuality_attendance_points(week)
        logging.info(f"Retrieved {len(attendance_results)} punctuality and attendance results for week {week}")

        #Get individual performance points
        performance_results = self.calculate_individual_rewards(week)
        logging.info(f"Retrieved {len(performance_results)} rewards results for week {week}")
        
        if encuesta_results:
            # Process and insert encuesta points into Points table
            encuesta_inserted, encuesta_duplicates = self._insert_points_to_database(encuesta_results, week)
        else:
            encuesta_inserted = 0
            encuesta_duplicates = 0

        if attendance_results:
            # Process and insert punctuality and attendance points into Points table
            attendance_inserted, attendance_duplicates = self._insert_points_to_database(attendance_results, week)
        else:
            attendance_inserted = 0
            attendance_duplicates = 0

        if performance_results:
            #Process and insert individual rewards into points table
            rewards_inserted, rewards_duplicates = self._insert_points_to_database(performance_results, week)
        else:
            rewards_inserted = 0
            rewards_duplicates = 0
            
        # Combine results for return value
        combined_results = {
            "encuesta": {
                "results": encuesta_results,
                "inserted": encuesta_inserted,
                "duplicates": encuesta_duplicates
            },
            "attendance_punctuality": {
                "results": attendance_results,
                "inserted": attendance_inserted,
                "duplicates": attendance_duplicates
            },
            "performance": {
                "results": performance_results, 
                "inserted": rewards_inserted, 
                "duplicates": rewards_duplicates 
            }
        }
        
        total_duplicates = encuesta_duplicates + attendance_duplicates + rewards_duplicates
        if total_duplicates > 0:
            logging.info(f"Total duplicate records skipped: {total_duplicates}")
        
        return combined_results

#Main function to run rewards procesor
def run_test(company_id, week, interval, multiplier=1.0, start_date=None, end_date=None):
    group_processor = GroupRewardProcessor(company_id, interval, multiplier)
    result = group_processor.process_rewards(week)
    logging.info(f"Processed {result['total_employees']} group rewards entries")
    logging.info(f"Inserted: {result['inserted']}, Duplicates skipped: {result['duplicates']}")
    
    individual_processor = IndividualRewardProcessor(company_id, interval, multiplier, start_date, end_date)
    results = individual_processor.process_rewards(week)
    
    logging.info(f"Processed {len(results['encuesta']['results'])} encuesta rewards entries")
    logging.info(f"Inserted: {results['encuesta']['inserted']}, Duplicates skipped: {results['encuesta']['duplicates']}")
    
    logging.info(f"Processed {len(results['attendance_punctuality']['results'])} attendance/punctuality rewards entries")
    logging.info(f"Inserted: {results['attendance_punctuality']['inserted']}, Duplicates skipped: {results['attendance_punctuality']['duplicates']}")
    
    

    