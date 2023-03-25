from datetime import datetime, timedelta

def increment_date(date_string):
    date = datetime.strptime(date_string, '%Y-%m-%d')
    incremented_date = date + timedelta(days=1)
    return incremented_date.strftime('%Y-%m-%d')

def is_date_before(date1_str, date2_str):
    # Convert the date strings to datetime objects
    date1 = datetime.strptime(date1_str, '%Y-%m-%d')
    date2 = datetime.strptime(date2_str, '%Y-%m-%d')

    # Check if date1 is before date2
    return date1 <= date2
    
def day_before(date_string):
    date = datetime.strptime(date_string, '%Y-%m-%d')
    day_before = date + timedelta(days=-1)
    return day_before.strftime('%Y-%m-%d')

def first_day_of_month(date_string):
    # Parse the input date string to a datetime object
    date = datetime.strptime(date_string, "%Y-%m-%d")
    
    year = date.year
    month = date.month
    
    first_day = datetime(year, month, 1)
    
    first_day_string = datetime.strftime(first_day, "%Y-%m-%d")
    
    return first_day_string

def month_before(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    first_day_of_month = date_obj.replace(day=1)
    last_month = first_day_of_month - timedelta(days=1)
    first_day_of_prior_month = last_month.replace(day=1)
    return first_day_of_prior_month.strftime('%Y-%m-%d')