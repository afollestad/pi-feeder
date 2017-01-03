#/usr/bin/python3

from tzlocal import get_localzone
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as reld

def add_days(to_date, days):
    return to_date + reld(days=days)

def subtract_days(to_date, days):
    return to_date - reld(days=days)

def right_now():
    return get_localzone().localize(dt.now())

def date_str(date):
    return date.strftime('%m/%d/%Y %H:%M')
    