from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
import os, smtplib, calendar
from email.mime.text import MIMEText

def loadTemplate():
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('email.txt')
    return template

def dateString(date):
    return date.strftime("%d %b %Y")

def calculateNextWeekday(date, weekday):
    days_until_next_weekday = 7 - date.weekday() + weekday
    next_weekday = (today + timedelta(days=days_until_next_weekday)).date()
    return dateString(next_weekday)

def getLooterName():
    return os.environ['LOOTER_NAME']

def getLooterEmail():
    return os.environ['LOOTER_EMAIL']

def getLootControllerEmail():
    return os.environ['LOOT_CONTROLLER_EMAIL']

def sendEmail(text):
    msg = MIMEText(text)
    msg['Subject'] = 'Motorcycle parking booking'
    msg['From'] = getLooterEmail()
    msg['To'] = getLootControllerEmail()
    msg['CC'] = getLooterEmail()
    s = smtplib.SMTP('localhost')
    s.sendmail(getLooterEmail(), getLootControllerEmail(), msg.as_string())
    s.quit()

calendar.setfirstweekday(calendar.MONDAY)
today = datetime.now()
variables = {}
variables['looter_name'] = getLooterName()
variables['start_date'] = calculateNextWeekday(today, calendar.MONDAY)
variables['end_date'] = calculateNextWeekday(today, calendar.FRIDAY)

sendEmail(loadTemplate().render(variables))
