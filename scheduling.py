#/usr/bin/python3

"""Scheduling read/write utils."""
import sqlite3
import threading
from time import sleep
from datetime import datetime as dt
from date_utils import *
from motor_util import MotorUtil
import sms
import prefs

IS_INIT = False

def day_diff(src, dst, next_week=False):
    if src == dst and next_week:
        return 7
    src = src + 1
    dst = dst + 1
    if dst > src:
        return dst - src
    count = 0
    index = 0
    while index != dst:
        count = count + 1
        index = index + 1
        if index > 6: 
            index = 0
    return count

def check_should_activate(recurrence):
    """Checks if the feeder should be activated right now."""
    now = right_now()
    return recurrence.year == now.year and recurrence.month == now.month and recurrence.day == now.day and recurrence.hour == now.hour and recurrence.minute == now.minute

def notify_phones_of_trigger():
    phones = prefs.get_phones()
    if len(phones) == 0:
        return
    body = 'The feeder has been triggered!'
    for num in phones:
        sms.send_sms(num, body)
    return

def ticker():
    """The ticker which checks if a schedule moment has been reached."""
    print("Started!")
    global IS_INIT
    while IS_INIT:
        try:
            next_occurrence = get_next_occurrence()
            if next_occurrence is not None:
                if check_should_activate(next_occurrence):
                    print("Schedule has triggered!")
                    # Remove one-time occurrence if any
                    remove_onetime_occurrence(next_occurrence.year, next_occurrence.month, next_occurrence.day, next_occurrence.hour, next_occurrence.minute)
                    if MotorUtil().turn_motor():
                        notify_phones_of_trigger()
            sleep(5)
        except KeyboardInterrupt:
            break
    print("Ticker has quit!")
    return

THREAD = threading.Thread(target=ticker)

def get_connection():
    """Gets a connection to the SQLite database."""
    return sqlite3.connect('pifeeder.db')

def init_scheduler():
    """Creates database tables if they don't already exist."""
    global IS_INIT
    if IS_INIT:
        print("Scheduler was already initialized!")
        return
    IS_INIT = True

    print("Setting up databases...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS recurrence (day_id INTEGER NOT NULL, hour INTEGER NOT NULL, minute INTEGER NOT NULL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS onetimes (year INTEGER NOT NULL, month INTEGER NOT NULL, day INTEGER NOT NULL, hour INTEGER NOT NULL, minute INTEGER NOT NULL)')
    conn.commit()
    conn.close()

    print("Starting ticker...")
    THREAD.start()
    return

def deinit_scheduler():
    global IS_INIT
    IS_INIT = False
    return

def get_recurrence_schedule():
    """Gets the ongoing daily recurrence schedule."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recurrence ORDER BY day_id, hour, minute')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_onetime_occurrence_schedule():
    """Gets the one-time ocurrence schedule."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM onetimes ORDER BY year, month, day, hour, minute')
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_occurrence(day_id, hour, minute):
    """Adds a recurrence to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM recurrence WHERE day_id = ? AND hour = ? AND minute = ?', (day_id, hour, minute))
    if cursor.fetchone() is not None:
        return False

    cursor.execute('INSERT INTO recurrence (day_id, hour, minute) VALUES (?, ?, ?);', (day_id, hour, minute))
    conn.commit()
    conn.close()
    return True

def remove_recurrence(day_id, hour, minute):
    """Remove a recurrence from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recurrence WHERE day_id = ? AND hour = ? AND minute = ?', (day_id, hour, minute))
    conn.commit()
    conn.close()
    return

def add_onetime_occurrence(year, month, day, hour, minute):
    """Adds a one-time ocurrence to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM onetimes WHERE year = ? AND month = ? AND day = ? AND hour = ? AND minute = ?', (year, month, day, hour, minute))
    if cursor.fetchone() is not None:
        return False

    cursor.execute('INSERT INTO onetimes (year, month, day, hour, minute) VALUES (?, ?, ?, ?, ?);', (year, month, day, hour, minute))
    conn.commit()
    conn.close()
    return True

def remove_onetime_occurrence(year, month, day, hour, minute):
    """Remove a onetime occurrence from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM onetimes WHERE year = ? AND month = ? AND day = ? AND hour = ? AND minute = ?', (year, month, day, hour, minute))
    conn.commit()
    conn.close()
    return

LAST_NEXT_OCCURENCE = None

def get_next_occurrence():
    next_recurrence = get_next_recurrence()
    next_onetime = get_next_onetime_occurrence()
    if next_recurrence is None:
        result = next_onetime
    elif next_onetime is None:
        result = next_recurrence
    elif next_onetime <= next_recurrence:
        result = next_onetime
    else:
        result = next_recurrence
    global LAST_NEXT_OCCURENCE
    if LAST_NEXT_OCCURENCE != result:
        print("Next occurrence:", result)
    LAST_NEXT_OCCURENCE = result
    return result

def get_next_recurrence():
    """Gets the next today/time for which the feeder will activate."""
    today = right_now()
    conn = get_connection()
    cursor = conn.cursor()

    # Try to find a next occurrence in the current week (before an ending Sunday).
    # Will be today within the remaining hours/minutes, or another day in the current week.
    cmd = '''SELECT * FROM recurrence WHERE 
        (day_id = {0} AND 
        hour >= {1} AND minute >= {2}) OR 
        (day_id > {0}) ORDER BY day_id, hour, minute'''.format(today.weekday(), today.hour, today.minute)
    cursor.execute(cmd)
    result = cursor.fetchone()

    if result is not None:
        # Found a next recurrence today, or within this week
        if result[0] == today.weekday():
            # today
            conn.close()
            target = dt(today.year, today.month, today.day, result[1], result[2])
            return target
        else:
            # after today
            days_diff = day_diff(today.weekday(), result[0])
            target = add_days(today, days=days_diff)
            conn.close()
            finalTarget = dt(target.year, target.month, target.day, result[1], result[2])
            return finalTarget

    if result is None:
        # Didn't find recurrence today or within the remaining week, check next week
        cmd = '''SELECT * FROM recurrence WHERE 
            (day_id < {0}) OR 
            (day_id = {0} AND hour = {1} AND minute < {2}) OR 
            (day_id = {0} AND hour < {1}) 
            ORDER BY day_id, hour, minute'''.format(today.weekday(), today.hour, today.minute)
        cursor.execute(cmd)
        result = cursor.fetchone()

        if result is not None:
            # Found a recurrence for previous week days, for next week
            days_diff = day_diff(today.weekday(), result[0], True)
            target = add_days(today, days_diff)
            conn.close()
            finalTarget = dt(target.year, target.month, target.day, result[1], result[2])
            return finalTarget

    conn.close()
    return None

def get_next_onetime_occurrence():
    """Gets the next one-time occurrence for which the feeder will activate."""
    today = right_now()
    conn = get_connection()
    cursor = conn.cursor()

    cmd = '''SELECT * FROM onetimes WHERE 
        (year >= {0}) OR
        (year = {0} AND month > {1}) OR 
        (year = {0} AND month = {1} AND day > {2}) OR 
        (year = {0} AND month = {1} AND day = {2} AND hour >= {3}) OR 
        (year = {0} AND month = {1} AND day = {2} AND hour = {3} AND minute >= {4})  
        ORDER BY year, month, day, hour, minute'''.format(today.year, today.month, today.day, today.hour, today.minute)

    cursor.execute(cmd)
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return None
    return dt(result[0], result[1], result[2], result[3], result[4])
