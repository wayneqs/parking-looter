import os
import smtplib
import calendar
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from dateutil.parser import parse
from jinja2 import Environment, FileSystemLoader

def day_in_week_format(value, fmt='medium'):
    """ Formats a date to day in week conventions """
    if fmt == 'full':
        fmt = "%a, %d %b %Y"
    elif fmt == 'medium':
        fmt = "%a (%d %b)"
    elif fmt == 'light':
        fmt = "%a"
    elif fmt == 'date':
        fmt = "%d %b %Y"
    return value.strftime(fmt)

def load_template():
    """ Loads the email template used for booking resources """
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['datetime'] = day_in_week_format
    env.trim_blocks = True
    template = env.get_template('email.txt')
    return template

def calculate_next_weekday(date, weekday):
    """ Calculates the next weekday from the specified date """
    days_until_next_weekday = 7 - date.weekday() + weekday
    next_weekday = (date + timedelta(days=days_until_next_weekday)).date()
    return day_in_week_format(next_weekday, 'date')

def get_looter_name():
    """ Returns the name of the person booking the resource """
    return os.environ['LOOTER_NAME']

def get_looter_email():
    """ Returns the email address of the person booking the resource """
    return os.environ['LOOTER_EMAIL']

def get_smtp_server():
    """ Returns the SMTP server address """
    return os.environ['MAIL_SERVER']

def get_loot_controller_email():
    """ Returns the email address of the person who controls the resource """
    return os.environ['LOOT_CONTROLLER_EMAIL']

def send_email(text):
    """ Sends an email with the body supplied """
    msg = MIMEText(text)
    msg['Subject'] = 'Motorcycle parking booking'
    msg['From'] = get_looter_email()
    msg['CC'] = get_looter_email()
    msg['To'] = get_loot_controller_email()
    smtp = smtplib.SMTP(get_smtp_server())
    smtp.sendmail(get_looter_email(), get_loot_controller_email(), msg.as_string())
    smtp.quit()

def load_holidays_in_range(start, end):
    """ Loads holidays from data file; past holidays are ignored """
    start = parse(start)
    end = parse(end)
    holidays = []
    if os.path.exists('holidays.dat'):
        with open('holidays.dat') as f:
            for line in f.readlines():
                date = parse(line)
                if date <= end and date >= start:
                    holidays.append(date)
    holidays.sort()
    return holidays

def run():
    """ Runs the looter process """
    calendar.setfirstweekday(calendar.MONDAY)
    today = datetime.now()
    variables = {}
    variables['looter_name'] = get_looter_name()
    variables['start_date'] = calculate_next_weekday(today, calendar.MONDAY)
    variables['end_date'] = calculate_next_weekday(today, calendar.FRIDAY)
    variables['holidays_in_period'] = load_holidays_in_range(variables['start_date'], variables['end_date'])
    if len(variables['holidays_in_period']) < 5:
        # 5 or more means that you are off for the week; so don't bother to
        # request a parking space
        send_email(load_template().render(variables))

run()
