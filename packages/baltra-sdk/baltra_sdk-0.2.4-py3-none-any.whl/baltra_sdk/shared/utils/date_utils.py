from datetime import datetime, timedelta

def convert_date(date_str):
    # Converts spanish input string to database compatible date YYYY-MM-DD
    # Example input: "10 de Mayo"
    months_in_spanish = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
        "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
        "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    day_str, _, month_str = date_str.partition(' de ')
    day = int(day_str.strip())
    month = months_in_spanish[month_str.strip()]

    # Decide the year (assumes date is in the future or this year)
    today = datetime.now()
    year = today.year
    if month < today.month:
        year += 1

    date_obj = datetime(year, month, day)
    return date_obj.strftime("%Y-%m-%d")


def get_latest_sunday_datetime():
    """Get the datetime of the latest Sunday."""
    today = datetime.today()
    days_to_sunday = (today.weekday() - 6) % 7
    latest_sunday = today - timedelta(days=days_to_sunday)
    latest_sunday = latest_sunday.replace(hour=23, minute=59, second=0, microsecond=0)
    return latest_sunday