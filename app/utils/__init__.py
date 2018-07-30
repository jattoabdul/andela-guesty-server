from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from .slackhelper import SlackHelper

db = SQLAlchemy()
slackhelper = SlackHelper()


def timestring_to_datetime(time_string):
	today = datetime.today()
	if time_string.find(':') > -1:
		time_string = time_string.split(':')
		time_string[1] = '59' if int(time_string[1]) > 59 else time_string[1]
		full_time_string = '{} {}, {} {}:{}'.format(today.day, today.month, today.year, time_string[0], time_string[1])
		return datetime.strptime(full_time_string, '%d %m, %Y %H:%M')
	else:
		return None


def prettify_datetime(datetime_obj):
	if datetime_obj is None:
		return {'default': None, 'date_pretty_short': None, 'date_pretty': None}
	else:
		return {'default': datetime_obj, 'date_pretty_short': datetime_obj.strftime('%b %d, %Y'), 'date_pretty': datetime_obj.strftime('%B %d, %Y')}
	
	
def time_format_12_24(datetime_obj):
	if datetime_obj is None:
		return {'default': None, 'date_pretty_short': None, 'date_pretty': None}
	else:
		meridian = 'AM' if int(datetime_obj.strftime('%H')) <= 11 else 'PM'
		return {'format_12': '{}{}'.format(datetime_obj.strftime('%b %d, %Y %I:%M'), meridian), 'format_24': datetime_obj.strftime('%b %d, %Y %H:%M')}
