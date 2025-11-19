from collections import defaultdict
import logging
from sqlalchemy import exc
from baltra_sdk.legacy.dashboards_folder.models import GroupRewards, RewardRules
from datetime import datetime, date, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)

class MetricsAreaPerformanceManager:
    """Manager of area performance metrics with integrated error handling"""
    DEFAULT_COLORS = ['#8884d8', '#82ca9d']

    
    def __init__(self, company_id: int):
        if not isinstance(company_id, int) or company_id <= 0:
            raise ValueError("Invalid company ID")
            
        self.company_id = company_id
        # self.six_months_ago = date.today() - timedelta(weeks=26)

    def get_available_areas(self) -> List[str]:
        """Retrieves list of unique areas for the company"""
        try:
            areas = GroupRewards.query.with_entities(
                GroupRewards.area
            ).filter_by(
                company_id=self.company_id
            ).distinct().order_by(
            GroupRewards.area.asc()
            ).all()
            
            return [area.area for area in areas] if areas else []
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error when fetching areas: {str(e)}")
            raise RuntimeError("Error retrieving areas from database")

    def _retrieve_area_metrics_data(self, area: str) -> List[Dict]:
        """Retrieves raw metrics data from the database"""
        try:
            results = GroupRewards.query.filter_by(
                company_id=self.company_id,
                area=area
            ).with_entities(
                GroupRewards.date,
                GroupRewards.score,
                GroupRewards.objective,
                GroupRewards.metric
            ).all()
            
            return [{
                'date': res.date,
                'score': res.score,
                'objective': res.objective,
                'metric': res.metric
            } for res in results]
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error for area {area}: {str(e)}")
            raise RuntimeError(f"Error retrieving metrics for area {area}")

    def process_area_metrics(self, area: str) -> List[Dict]:
        """Processes metrics and generates visualization structure"""
        try:
            raw_data = self._retrieve_area_metrics_data(area)
            return self._transform_metrics_data(raw_data, area)
            
        except RuntimeError as e:
            logger.error(f"Error processing area {area}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing area {area}: {str(e)}")
            raise RuntimeError("Internal error processing metrics")

    def _transform_metrics_data(self, raw_data: List[Dict], area: str) -> List[Dict]:
        """Transforms raw data into frontend structure"""
        metrics_dict = defaultdict(lambda: {"list": [], "sub_points": 0})

        
        for entry in raw_data:
            metric_key = entry['metric']
            score = entry['score']
            objective = entry['objective']
            
            if score > 100:
                score = round((score / objective) * 100, 2)
            
            if objective > 100:
                objective = 100
                
            
            metrics_dict[metric_key]["list"].append({
                'date': entry['date'].strftime('%Y-%m-%d'),
                'score': round(score, 2),
                'objective': round(objective, 2),
                'objective-value': entry['objective']
            })
            
        for metric, entries in metrics_dict.items():
            try:
              self._process_metric_rules(metric, entries, area)
            except:
                # Ensure we always return the entries even if rules retrieval fails
                pass
          
        
        return [
            self._create_metric_structure(metric, entries)
            for metric, entries in metrics_dict.items()
        ]

    def _create_metric_structure(self, metric: str, entries: List[Dict]) -> Dict:
        """Creates final structure for each individual metric"""
        try:
            sorted_entries = sorted(
                entries["list"],
                key=lambda x: self._parse_date_string(x['date']),
            )
            
            return {
                'title': metric,
                'description': 'Objetivos vs Puntuación',
                'companyId': self.company_id,
                'data': sorted_entries,
                'xAxisLabel': 'Semana',
                'yAxisLabel': 'Puntuación',
                'lines': self._generate_chart_lines(entries["sub_points"])
            }
            
        except (KeyError, ValueError) as e:
            logger.error(f"Error formatting metric {metric}: {str(e)}")
            raise ValueError(f"Inconsistent data for metric {metric}")
          
          
    def _generate_chart_lines(self, sub_points: Dict[str, int]) -> List[Dict]:
        """Generates line configuration for the chart"""
        base_lines = [
            # {'dataKey': 'objective', 'name': 'Objetivo', 'color': self.DEFAULT_COLORS[0]},
            {'dataKey': 'score', 'name': 'Puntuación', 'color': self.DEFAULT_COLORS[1]}
        ]
        colors = generate_vibrant_colors(len(sub_points))
        
        sub_lines = [
            {
                'dataKey': key,
                'name': f'{value} puntos',
                'color': colors[i]
            }
            for i, (key, value) in enumerate(sub_points.items())
            if value != 0
        ]


        return base_lines + sub_lines
          
    def _process_metric_rules(self, metric: str, entries: Dict, area: str):
        """Process reward rules for a specific metric"""
        try:
            rules = self.get_rules_by_metric(area, metric)
            thresholds, points = self._get_thresholds_from_rules(rules)
            dictPoints = {}
            
            for entry in entries["list"]:
                all_subs_gt_50 = all(threshold < 5 for threshold in thresholds)
                for i, threshold in enumerate(thresholds, 1):
                  if threshold == 0 or threshold == 100:
                    continue
                  entry[f'sub_objective_{i}'] = threshold
                  dictPoints[f'sub_objective_{i}'] = points[threshold]
                if all_subs_gt_50:
                  entry["objective"] = 0
                    
            entries["sub_points"] = dictPoints

        except Exception as e:
            logger.warning(f"Reglas no aplicadas para {metric}: {str(e)}")

    @staticmethod
    def _parse_date_string(date_str: str) -> datetime:
        """Attempts to parse different date formats"""
        for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unrecognized date format: {date_str}")


    def get_rules_by_metric(self, area: str, metric: str) -> List[Dict]:
        """Get rules associated with a specific area and metric"""
        try:
            result = RewardRules.query.filter_by(
                company_id=self.company_id,
                area=area,
                metric_name=metric
            ).with_entities(RewardRules.points_json).first()

            if not result or not result[0]:
                return []

            return result[0].get('steps', [])[1:]  # Excluir primer elemento
        except exc.SQLAlchemyError as e:
            logger.error(f"Error en BD para {area}/{metric}: {str(e)}")
            raise RuntimeError(f"Error obteniendo reglas para {area}/{metric}")

    @staticmethod
    def _get_thresholds_from_rules(rules: List[Dict]) -> tuple[List[int], Dict[int, int]]:
        """Extracts unique thresholds from rules and their corresponding points in order"""
        thresholds = set()
        points_map = defaultdict(int)

        for rule in rules:
            if 'min' in rule:
                thresholds.add(rule['min'])
                points_map[rule['min']] = rule['points']
            if 'max' in rule:
                thresholds.add(rule['max'])
                points_map[rule['max']] = rule['points']
                
        return sorted(thresholds), points_map

def generate_vibrant_colors(count: int) -> List[str]:
    colors: List[str] = []

    for i in range(count):
        hue: float = (360 / count) * i
        saturation: float = 0.9
        lightness: float = 0.55

        c: float = (1 - abs(2 * lightness - 1)) * saturation
        x: float = c * (1 - abs((hue / 60) % 2 - 1))
        m: float = lightness - c / 2

        if 0 <= hue < 60:
            r1, g1, b1 = c, x, 0
        elif 60 <= hue < 120:
            r1, g1, b1 = x, c, 0
        elif 120 <= hue < 180:
            r1, g1, b1 = 0, c, x
        elif 180 <= hue < 240:
            r1, g1, b1 = 0, x, c
        elif 240 <= hue < 300:
            r1, g1, b1 = x, 0, c
        else:
            r1, g1, b1 = c, 0, x

        r, g, b = [int((val + m) * 255) for val in (r1, g1, b1)]
        hex_color: str = f"#{r:02X}{g:02X}{b:02X}"
        colors.append(hex_color)

    return colors